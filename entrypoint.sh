#!/bin/bash
set -e
set -x  # for debug logging

# Explicitly set the Django settings module if not already set
# This ensures it's set correctly even if Cloud Run environment variables aren't properly passed
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-xblock.settings.production}

# Print current Django settings module for debugging
echo "Using Django settings module: $DJANGO_SETTINGS_MODULE"

# Optional: wait for DB to be ready
python manage.py wait_for_db || echo "Database not ready, continuing..."

# Collect static files
python manage.py collectstatic --noinput || echo "collectstatic failed"

# Apply migrations
python manage.py migrate || echo "migrate failed"

# Validate Django settings before starting server
python -c "import django; django.setup(); from django.conf import settings; print(f'Django settings loaded successfully. DEBUG={settings.DEBUG}')" || echo "Django settings validation failed"

# Start Gunicorn server
exec gunicorn xblock.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 300 \
    --log-level=info
