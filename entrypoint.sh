#!/bin/sh

# Apply database migrations (optional, but good practice)
# For this minimal setup, we don't expect migrations, but the command can be included.
# python manage.py migrate --noinput

# Start Gunicorn server
# Use the PORT environment variable, default to 8080 if not set.
# The --workers flag can be adjusted based on the Cloud Run instance's CPU.
# For a minimal setup, 2-4 workers are usually fine.
# Gunicorn should bind to 0.0.0.0 to be accessible from outside the container.
gunicorn xblock.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 3 \
    --log-level info \
    --access-logfile '-' \
    --error-logfile '-'

echo "Entrypoint script finished."
