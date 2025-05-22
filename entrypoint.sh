#!/bin/bash
set -e

# Load environment variables from .env file if it exists (for local development)
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if we're running in Cloud Run (environment variables will be set via Secret Manager)
if [ -z "$K_SERVICE" ]; then
    echo "Running in local environment"
else
    echo "Running in Cloud Run environment with service: $K_SERVICE"
fi

# Wait for database to be ready
echo "Waiting for database connection..."
MAX_RETRIES=10
COUNT=0
until python -c "import psycopg2; psycopg2.connect(host='$DATABASE_HOST', port='$DATABASE_PORT', dbname='$DATABASE_NAME', user='$DATABASE_USER', password='$DATABASE_PASSWORD')" 2>/dev/null; do
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "Could not connect to database after $MAX_RETRIES attempts. Exiting."
        exit 1
    fi
    echo "Database connection attempt $COUNT of $MAX_RETRIES failed. Retrying in 5 seconds..."
    sleep 5
done
echo "Database connection successful!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn xblock.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 60
