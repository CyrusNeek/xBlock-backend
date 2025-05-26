#!/bin/bash
# This script starts the Django application in Cloud Run

# Exit immediately if a command exits with a non-zero status
set -e

# Print debug info to help troubleshoot
echo "===== STARTING ENTRYPOINT.SH ====="
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Python version: $(python --version)"
echo "Pip packages: $(pip list)"

# Explicitly set the Django settings module if not already set
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-xblock.settings.production}
echo "Using Django settings module: $DJANGO_SETTINGS_MODULE"

# Make sure PORT is set for Cloud Run
export PORT=${PORT:-8080}
echo "Using PORT: $PORT"

# Print environment variables for debugging (excluding secrets)
echo "Environment variables:"
env | grep -v -E "SECRET|PASSWORD|KEY" | sort

# Check if Django can be imported
echo "Checking Django installation..."
python -c "import django; print(f'Django version: {django.get_version()}')" || { echo "ERROR: Django not installed properly"; exit 1; }

# Check if the wsgi module can be imported
echo "Checking WSGI configuration..."
python -c "import xblock.wsgi" || { echo "ERROR: Cannot import xblock.wsgi"; exit 1; }

# Wait for database to be ready (with timeout)
echo "Waiting for database connection..."
python manage.py wait_for_db || { echo "WARNING: Database not ready, but continuing..."; }

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || { echo "WARNING: Static file collection failed"; }

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate || { echo "WARNING: Database migration failed"; }

# Validate Django settings before starting server
echo "Validating Django settings..."
python -c "import django; django.setup(); from django.conf import settings; print(f'Django settings loaded successfully. DEBUG={settings.DEBUG}')" || { echo "ERROR: Django settings validation failed"; exit 1; }

# Start Gunicorn server optimized for Cloud Run
echo "===== STARTING GUNICORN SERVER ====="
exec gunicorn xblock.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --worker-class gthread \
    --workers 1 \
    --threads 8 \
    --timeout 0 \
    --graceful-timeout 30 \
    --keep-alive 60 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output

# This line will only execute if exec gunicorn fails
echo "ERROR: Gunicorn execution failed. Container will now exit."
exit 1
