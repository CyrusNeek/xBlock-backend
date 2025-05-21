#!/bin/bash

echo "🔐 Loading secrets from /secrets/backend.env"
if [ -f /secrets/backend.env ]; then
  export $(cat /secrets/backend.env | xargs)
else
  echo "❌ backend.env not found"
  exit 1
fi

echo "⚙️ Running Django migrations..."
python manage.py migrate --noinput || exit 1

echo "🚀 Starting Gunicorn..."
exec gunicorn web.wsgi:application --bind 0.0.0.0:$PORT
echo "✅ Starting deployment on $(date)"
