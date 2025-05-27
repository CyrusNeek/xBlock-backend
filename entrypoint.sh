#!/bin/bash
# This script starts the Django application in Cloud Run

# Exit on error, but allow certain commands to fail
set -e

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
# System information
log "System Information:"
log "Current directory: $(pwd)"
log "Directory contents: $(ls -la)"
log "Python version: $(python --version)"
log "Pip packages: $(pip list)"

# Check required environment variables
log "Checking required environment variables..."
check_required_var "DJANGO_SETTINGS_MODULE" || exit 1
check_required_var "DATABASE_NAME" || exit 1
check_required_var "DATABASE_USER" || exit 1
check_required_var "DATABASE_PASSWORD" || exit 1
check_required_var "DATABASE_HOST" || exit 1

# Set default values
export PORT=${PORT:-8080}
log "Using PORT: $PORT"

# Print non-sensitive environment variables
log "Environment variables (excluding secrets):"
env | grep -v -E "SECRET|PASSWORD|KEY" | sort

# Verify Python environment
log "Verifying Python environment..."
python -c "import django; print(f'Django {django.get_version()} installed successfully')" || { log "ERROR: Django not installed properly"; exit 1; }

# Test database connection
log "Testing database connection..."
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

# Run database migrations
log "Running database migrations..."
python manage.py migrate --noinput || { log "ERROR: Database migration failed"; exit 1; }

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput || { log "WARNING: Static file collection failed"; }

# Validate Django settings
log "Validating Django settings..."
python -c "import django; django.setup(); from django.conf import settings; print(f'Settings validated. DEBUG={settings.DEBUG}')" || { log "ERROR: Settings validation failed"; exit 1; }

# Start Gunicorn with Cloud Run optimized settings
log "===== STARTING GUNICORN SERVER ====="
exec gunicorn xblock.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --worker-class gthread \
    --workers 1 \
    --threads 8 \
    --timeout 0 \
    --graceful-timeout 30 \
    --keep-alive 60 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --preload \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-file - \
    --logger-class gunicorn.glogging.Logger

# This line will only execute if exec gunicorn fails
log "ERROR: Gunicorn execution failed"
exit 1
