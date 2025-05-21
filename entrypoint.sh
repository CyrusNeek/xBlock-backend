#!/bin/bash

echo "🧪 entrypoint.sh started at $(date)"

# Load secrets
if [ -f /secrets/backend.env ]; then
  echo "🔐 Loading secrets from /secrets/backend.env"
  export $(cat /secrets/backend.env | xargs)
else
  echo "❌ /secrets/backend.env NOT FOUND"
  exit 1
fi

# Debug Python path and env
echo "🐍 PYTHONPATH: $PYTHONPATH"
echo "🔧 DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Manually run Django shell to catch error
echo "🧪 Running isolated import check..."
python -c "import django; django.setup(); from django.apps import apps; apps.populate(apps.app_configs)" || exit 1

# Continue if successful
echo "✅ Django import check passed. Running migrations..."
python manage.py migrate --noinput || exit 1

echo "🚀 Starting Gunicorn..."
exec gunicorn web.wsgi:application --bind 0.0.0.0:$PORT
