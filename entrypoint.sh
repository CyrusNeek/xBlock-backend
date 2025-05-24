#!/bin/bash
# Enable command echoing for debugging
set -e
set -x

# Print environment (without passwords)
echo "============ ENVIRONMENT VARIABLES ============"
env | grep -v -E 'PASSWORD|SECRET|KEY' | sort

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
    
    # Create directory for credentials if it doesn't exist
    mkdir -p /tmp/keys
    
    # Write GCP credentials to file if provided as environment variable
    if [ ! -z "$GCP_CREDENTIALS" ]; then
        echo "Writing GCP credentials to file..."
        echo "$GCP_CREDENTIALS" > /tmp/keys/gcp-credentials.json
        echo "GCP credentials written to /tmp/keys/gcp-credentials.json"
    else
        echo "WARNING: GCP_CREDENTIALS environment variable not set"
    fi
fi

# Wait for database to be ready
echo "Waiting for database connection..."
MAX_RETRIES=20
COUNT=0

# Debug database connection parameters (without showing the password)
echo "Database connection parameters:"
echo "  HOST: $DATABASE_HOST"
echo "  PORT: $DATABASE_PORT"
echo "  NAME: $DATABASE_NAME"
echo "  USER: $DATABASE_USER"
until python -c "import psycopg2; print('Attempting to connect to database...'); conn = psycopg2.connect(host='$DATABASE_HOST', port='$DATABASE_PORT', dbname='$DATABASE_NAME', user='$DATABASE_USER', password='$DATABASE_PASSWORD'); print('Connection successful!'); conn.close()"; do
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
python manage.py migrate --noinput || { echo "Migration failed!"; exit 1; }

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || { echo "Collectstatic failed!"; exit 1; }

# Check if wsgi.py exists
echo "Checking for wsgi.py..."
if [ ! -f "xblock/wsgi.py" ]; then
    echo "ERROR: wsgi.py not found at xblock/wsgi.py"
    find . -name "wsgi.py" -type f
    exit 1
fi

# Start Gunicorn server
echo "Starting Gunicorn server..."
echo "Using PORT=${PORT:-8080}"
exec gunicorn xblock.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 60 --log-level debug
