#!/bin/bash
# This script starts the Django application in Cloud Run

# Exit on error and print each command
set -ex

# Function to log to stderr for Cloud Run logging
log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $1" >&2
}

# Function to dump environment (excluding secrets)
dump_env() {
    log "Environment variables (excluding secrets):"
    env | grep -v -E "SECRET|PASSWORD|KEY" | sort >&2
}

# Print Python and system info
print_debug_info() {
    log "Python version: $(python --version)"
    log "Python path: $PYTHONPATH"
    log "Current directory: $(pwd)"
    log "Directory contents: $(ls -la)"
    log "Django settings module: $DJANGO_SETTINGS_MODULE"
    log "Port: ${PORT:-8080}"
}

# Function to log messages with timestamps
log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $1"
}

# Function to check if a secret/env var is set
check_required_var() {
    if [ -z "${!1}" ]; then
        log "ERROR: Required environment variable $1 is not set"
        return 1
    fi
    log "✓ $1 is set"
    return 0
}

log "===== STARTING ENTRYPOINT.SH ====="
# Print initial debug info
log "=== STARTUP DIAGNOSTICS ==="
print_debug_info
dump_env

# Check required environment variables
log "=== CHECKING ENVIRONMENT ==="
required_vars=(
    "DJANGO_SETTINGS_MODULE"
    "DATABASE_NAME"
    "DATABASE_USER"
    "DATABASE_PASSWORD"
    "DATABASE_HOST"
    "PORT"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log "ERROR: Required environment variable $var is not set"
        exit 1
    fi
    log "✓ $var is set"
done

# Verify Python environment
log "=== CHECKING PYTHON ==="
if ! python -c "import sys; print(f'Python {sys.version} loaded successfully')"; then
    log "ERROR: Python environment check failed"
    exit 1
fi

# Verify Django installation
log "=== CHECKING DJANGO ==="
if ! python -c "import django; print(f'Django {django.get_version()} installed successfully')"; then
    log "ERROR: Django not installed properly"
    exit 1
fi

# Test WSGI module import
log "=== CHECKING WSGI ==="
if ! python -c "import xblock.wsgi; print('WSGI module loaded successfully')"; then
    log "ERROR: Cannot import WSGI module"
    exit 1
fi

# Test settings module
log "=== CHECKING SETTINGS ==="
if ! python -c "import django; django.setup(); from django.conf import settings; print(f'Settings loaded. DEBUG={settings.DEBUG}')"; then
    log "ERROR: Cannot load Django settings"
    exit 1
fi

# Test database connection
log "=== CHECKING DATABASE ==="
python << END
import os
from django.db import connections
from django.db.utils import OperationalError

print(f"Attempting to connect to {os.environ.get('DATABASE_NAME')} at {os.environ.get('DATABASE_HOST')}")
try:
    conn = connections['default']
    conn.ensure_connection()
    print("Database connection successful!")
except OperationalError as e:
    print(f"Database connection failed: {e}")
    exit(1)
END

# Collect static files (non-blocking)
log "=== COLLECTING STATIC FILES ==="
python manage.py collectstatic --noinput || log "WARNING: Static file collection failed"

# Run migrations (optional in Cloud Run)
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    log "=== RUNNING MIGRATIONS ==="
    python manage.py migrate --noinput || { log "ERROR: Database migration failed"; exit 1; }
fi

# Start Gunicorn
log "=== STARTING GUNICORN ==="
log "Binding to 0.0.0.0:${PORT}"

# Test port availability
if ! python -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', ${PORT})); s.close()"; then
    log "ERROR: Port ${PORT} is not available"
    exit 1
fi

# Start with minimal config first
exec gunicorn xblock.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --worker-class gthread \
    --workers 1 \
    --threads 4 \
    --timeout 30 \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --capture-output \
    --logger-class gunicorn.glogging.Logger \
    --log-file - \
    --preload

# This line will only execute if gunicorn fails
log "ERROR: Gunicorn execution failed"
exit 1
