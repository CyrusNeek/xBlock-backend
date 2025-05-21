#!/bin/bash

echo "🧪 entrypoint.sh started at $(date)"

# Load secrets
if [ -f /secrets/backend.env ]; then
  echo "🔐 Loading secrets from /secrets/backend.env (using 'source')"
  # Ensure lines are processed correctly, ignoring comments and trimming whitespace
  # and handling various shell quoting.
  set -o allexport # Export all subsequent variable assignments that don't have export already
  source /secrets/backend.env # Source the .env file
  set +o allexport # Stop automatically exporting
  echo "✅ Secrets loaded from /secrets/backend.env"
else
  # This path might be taken if Cloud Run is injecting environment variables directly
  # and the file mount is not used or is a fallback.
  # For now, we assume the file is critical for this setup.
  echo "❌ CRITICAL: /secrets/backend.env NOT FOUND. Deployment requires this file for secret loading."
  exit 1 # Exit if the secret file is not found, as per current design
fi

# Debug Python path and env
echo "🐍 PYTHONPATH: $PYTHONPATH"
# Explicitly set DJANGO_SETTINGS_MODULE for clarity and to ensure it's correct
export DJANGO_SETTINGS_MODULE="xblock.settings"
echo "🔧 Explicitly set DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

echo "🧪 Running isolated import check with settings.LOGGING print attempt..."
# Prepare a Python command to print settings.LOGGING then run django.setup()
# This helps diagnose if settings are loaded correctly and what LOGGING looks like.
PYTHON_CMD="
import os
print('--- Attempting to print settings.LOGGING ---')
try:
    # DJANGO_SETTINGS_MODULE should be set in the environment by now
    from django.conf import settings
    import pprint
    # Ensure LOGGING attribute exists before trying to print it
    if hasattr(settings, 'LOGGING'):
        print('settings.LOGGING content:')
        pprint.pprint(settings.LOGGING)
    else:
        print('settings.LOGGING attribute not found.')
except Exception as e:
    print(f'Error accessing django.conf.settings or printing LOGGING: {e}')
    print('Listing imported modules to check for django availability:')
    import sys
    pprint.pprint(sys.modules.keys())

print('--- Proceeding with django.setup() ---')
import django
django.setup()
from django.apps import apps
apps.populate(apps.app_configs)
"

python -c "${PYTHON_CMD}" || exit 1

# Continue if successful
echo "✅ Django import check passed. Running migrations..."
python manage.py migrate --noinput || exit 1

echo "🚀 Starting Gunicorn..."
exec gunicorn web.wsgi:application --bind 0.0.0.0:$PORT
