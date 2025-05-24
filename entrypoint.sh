#!/bin/bash
set -e
set -x  # for debug logging

# Optional: wait for DB to be ready
python manage.py wait_for_db || echo "Database not ready, continuing..."

# Collect static files
python manage.py collectstatic --noinput || echo "collectstatic failed"

# Apply migrations
python manage.py migrate || echo "migrate failed"

# Start Gunicorn server
exec gunicorn xblock.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --log-level=info
