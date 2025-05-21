#!/bin/bash

echo "🧪 entrypoint.sh started at $(date)"

if [ -f /secrets/backend.env ]; then
  echo "🔐 Loading secrets from /secrets/backend.env"
  export $(cat /secrets/backend.env | xargs)
else
  echo "❌ /secrets/backend.env not found!"
  exit 1
fi

echo "⚙️ Running Django check..."
python manage.py check || exit 1

echo "⚙️ Running Django migrations..."
python manage.py migrate --noinput || exit 1

echo "🚀 Starting Gunicorn..."
exec gunicorn web.wsgi:application --bind 0.0.0.0:$PORT
