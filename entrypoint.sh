#!/bin/bash

echo "🔐 Loading secrets from /secrets/backend.env"
if [ -f /secrets/backend.env ]; then
  export $(cat /secrets/backend.env | xargs)
fi

echo "⚙️ Running Django migrations..."
python manage.py migrate --noinput

echo "🚀 Starting Gunicorn..."
exec gunicorn web.wsgi:application --bind 0.0.0.0:$PORT
