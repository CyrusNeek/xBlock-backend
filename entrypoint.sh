#!/bin/bash

# 🔐 Secrets are now loaded from environment variables set by GCP Secret Manager and Cloud Run settings.

echo "⚙️ Running Django migrations..."
python manage.py migrate --noinput

echo "🚀 Starting Gunicorn..."
exec gunicorn web.wsgi:application --bind 0.0.0.0:$PORT
