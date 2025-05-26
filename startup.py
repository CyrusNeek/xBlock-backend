#!/usr/bin/env python
"""
Startup script for xblock application.
"""

import os
import sys
import time
import logging
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

def load_secrets():
    """Load secrets from mounted .env file."""
    try:
        env_path = Path('/app/.env')
        if env_path.exists():
            logger.info("Loading secrets from .env file")
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
            logger.info("Secrets loaded successfully")
        else:
            logger.warning("No .env file found at /app/.env")
            logger.info(f"Contents of /app directory: {os.listdir('/app')}")
    except Exception as e:
        logger.error(f"Error loading secrets: {str(e)}")
        logger.error(traceback.format_exc())

def check_database():
    """Check if the default database is available."""
    try:
        import django
        from django.db import connections
        connections['default'].cursor()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def main():
    try:
        start_time = time.time()
        logger.info("=== Starting xblock application ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current working directory: {os.getcwd()}")

        # Load secrets
        load_secrets()

        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xblock.settings.production')
        logger.info(f"DJANGO_SETTINGS_MODULE set to {os.environ['DJANGO_SETTINGS_MODULE']}")

        # Initialize Django
        import django
        django.setup()
        logger.info("Django setup completed")

        # Check database connection (retry up to 5 times)
        retries = 5
        while retries > 0:
            if check_database():
                break
            retries -= 1
            if retries > 0:
                logger.info(f"Retrying database connection in 5s... ({retries} attempts left)")
                time.sleep(5)
            else:
                logger.error("Failed to connect to database after all retries")
                sys.exit(1)

        # Run migrations
        logger.info("Running migrations...")
        from django.core.management import call_command
        call_command('migrate', '--noinput')

        # Collect static files
        logger.info("Collecting static files...")
        call_command('collectstatic', '--noinput', verbosity=0)

        # Start Gunicorn to serve Django app
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting Gunicorn on 0.0.0.0:{port}")
        from gunicorn.app.wsgiapp import WSGIApplication
        sys.argv = [
            "gunicorn",
            "xblock.wsgi:application",
            "--bind", f"0.0.0.0:{port}",
            "--worker-class", "gthread",
            "--workers", "1",
            "--threads", "4",
            "--timeout", "120",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "--log-level", "info"
        ]
        WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()

        logger.info(f"Startup completed in {time.time() - start_time:.2f}s")

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main()
