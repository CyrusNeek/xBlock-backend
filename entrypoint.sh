#!/bin/bash
set -e

# Enable command tracing for debugging
set -x

# Print environment (without passwords)
echo "============ ENVIRONMENT VARIABLES ============"
env | grep -v -E 'PASSWORD|SECRET|KEY' | sort

# Load environment variables from .env file if it exists (for local development)
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if we're running in Cloud Run
if [ ! -z "$K_SERVICE" ]; then
    echo "Running in Cloud Run environment with service: $K_SERVICE"
    
    # Create directory for credentials if it doesn't exist
    mkdir -p /tmp/keys
    
    # Write GCP credentials to file if provided as environment variable
    if [ ! -z "$GCP_CREDENTIALS" ]; then
        echo "Writing GCP credentials to file..."
        echo "$GCP_CREDENTIALS" > /tmp/keys/gcp-credentials.json
        echo "GCP credentials written to /tmp/keys/gcp-credentials.json"
    fi
fi

# Wait for database to be ready
echo "Waiting for database connection..."
MAX_RETRIES=10
COUNT=0

until python -c "import psycopg2; conn = psycopg2.connect(host='$DATABASE_HOST', port='$DATABASE_PORT', dbname='$DATABASE_NAME', user='$DATABASE_USER', password='$DATABASE_PASSWORD'); conn.close()" || [ $COUNT -eq $MAX_RETRIES ]; do
    COUNT=$((COUNT+1))
    if [ $COUNT -eq $MAX_RETRIES ]; then
        echo "Could not connect to database after $MAX_RETRIES attempts. Starting server anyway..."
        break
    fi
    echo "Database connection attempt $COUNT of $MAX_RETRIES failed. Retrying in 5 seconds..."
    sleep 5
done

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static files collection failed, but continuing..."

# Apply database migrations if database is available
if [ $COUNT -lt $MAX_RETRIES ]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput || echo "Migration failed, but continuing..."
fi

# Check for WSGI file
echo "Checking for WSGI file..."
WSGI_PATH="xblock.wsgi:application"
if [ ! -f "xblock/wsgi.py" ]; then
    echo "WARNING: wsgi.py not found at xblock/wsgi.py"
    # Try to find it elsewhere
    WSGI_FILE=$(find . -name "wsgi.py" -type f | head -1)
    if [ -z "$WSGI_FILE" ]; then
        echo "ERROR: No wsgi.py file found in the project"
        exit 1
    else
        # Convert path like ./config/wsgi.py to config.wsgi:application
        WSGI_PATH=$(echo $WSGI_FILE | sed 's/^\.\/\(.*\)\/wsgi\.py$/\1.wsgi:application/')
        echo "Found WSGI file at $WSGI_FILE, using $WSGI_PATH"
    fi
fi

# Start Gunicorn server
echo "Starting Gunicorn server on port ${PORT:-8080} with WSGI path $WSGI_PATH"
exec gunicorn $WSGI_PATH \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 3 \
    --threads 8 \
    --timeout 120 \
    --log-level debug
