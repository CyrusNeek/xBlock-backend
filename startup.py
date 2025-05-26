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
            # List contents of /app directory for debugging
            logger.info(f"Contents of /app directory: {os.listdir('/app')}")
    except Exception as e:

def run_migrations():
    """Run Django migrations."""
    try:
        logger.info("Running Django migrations")
        django.setup()
        from django.core.management import call_command
        call_command('migrate', '--noinput')
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

def test_port_binding(port):
    """Test if we can bind to the port."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', port))
        logger.info(f"Successfully bound to port {port}")
        sock.close()
        return True
    except Exception as e:
        logger.error(f"Could not bind to port {port}: {str(e)}")
        return False
    finally:
        sock.close()

def main():
    """Main startup function."""
    try:
        start_time = time.time()
        logger.info("=== Starting xblock application ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current working directory: {os.getcwd()}")

        # Get port from environment
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Using port: {port}")

        # Test port binding
        if not test_port_binding(port):
            logger.error("Port binding test failed")
            sys.exit(1)

        # Load secrets
        if not load_secrets():
            sys.exit(1)

        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xblock.settings.production')
        logger.info(f"DJANGO_SETTINGS_MODULE set to {os.environ['DJANGO_SETTINGS_MODULE']}")

        # Import Django and initialize
        import django
        django.setup()
        logger.info("Django setup completed")

        # Verify Django settings
        from django.conf import settings
        logger.info(f"Django settings verification:")
        logger.info(f"  DEBUG: {settings.DEBUG}")
        logger.info(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        logger.info(f"  STATIC_ROOT: {settings.STATIC_ROOT}")
        logger.info(f"  DATABASES: {settings.DATABASES['default']['ENGINE']}")

        # Run migrations (but don't fail if they fail)
        run_migrations()

        # Verify Django settings
        from django.conf import settings
        logger.info(f"Django settings verification:")
        logger.info(f"  DEBUG: {settings.DEBUG}")
        logger.info(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        logger.info(f"  STATIC_ROOT: {settings.STATIC_ROOT}")
        logger.info(f"  DATABASES: {settings.DATABASES['default']['ENGINE']}")
        logger.info(f"  INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}")

        # Collect static files
        from django.core.management import call_command
        logger.info("Collecting static files...")
        call_command('collectstatic', '--noinput', verbosity=0)
        logger.info("Static files collected successfully")

        # Configure Gunicorn
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key, value)

            def load(self):
                return self.application

        # Get port from environment
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting server on port {port}")

        # Initialize Django
        django.setup()

        # Check database connection
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
        django.core.management.call_command('migrate', '--noinput')

        # Collect static files
        logger.info("Collecting static files...")
        django.core.management.call_command('collectstatic', '--noinput')

        # Configure Gunicorn options
        options = {
            'bind': f'0.0.0.0:{port}',
            'worker_class': 'gthread',
            'workers': 1,
            'threads': 4,
            'timeout': 0,
            'keepalive': 2,
            'accesslog': '-',
            'errorlog': '-',
            'loglevel': 'info',
            'capture_output': True,
            'enable_stdio_inheritance': True,
            'preload_app': False,
            'reload': False,
            'max_requests': 0,
            'max_requests_jitter': 0
        }

        # Create a health check application
        health_app = create_health_check_app()

        logger.info(f"Startup completed in {time.time() - start_time:.2f}s")
        logger.info("Starting Gunicorn server...")
        StandaloneApplication(health_app, options).run()

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main() 