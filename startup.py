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
        logger.error(f"Error loading secrets: {str(e)}")
        raise

def run_migrations():
    """Run Django migrations."""
    try:
        logger.info("Running Django migrations")
        from django.core.management import call_command
        call_command('migrate', '--noinput')
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise

def main():
    """Main startup function."""
    try:
        # Print startup information
        logger.info("=== Starting xblock application ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Directory contents: {os.listdir('.')}")
        logger.info(f"Environment variables: {dict(os.environ)}")
        logger.info(f"Process ID: {os.getpid()}")
        logger.info(f"User ID: {os.getuid() if hasattr(os, 'getuid') else 'N/A'}")
        logger.info(f"Group ID: {os.getgid() if hasattr(os, 'getgid') else 'N/A'}")

        # Load secrets
        load_secrets()

        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xblock.settings.production')
        logger.info(f"DJANGO_SETTINGS_MODULE set to {os.environ['DJANGO_SETTINGS_MODULE']}")

        # Run migrations
        run_migrations()

        # Import Django
        import django
        django.setup()
        logger.info("Django setup completed")

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

        # Configure Gunicorn options
        options = {
            'bind': f'0.0.0.0:{port}',
            'workers': 2,
            'threads': 2,
            'timeout': 30,
            'keepalive': 5,
            'worker_class': 'gthread',
            'accesslog': '-',
            'errorlog': '-',
            'loglevel': 'info',
            'capture_output': True,
            'enable_stdio_inheritance': True,
            'preload_app': True,
            'graceful_timeout': 120,
            'max_requests': 1000,
            'max_requests_jitter': 50,
            'worker_connections': 1000,
            'backlog': 2048,
        }

        logger.info("Gunicorn configuration:")
        for key, value in options.items():
            logger.info(f"  {key}: {value}")

        # Start Gunicorn
        from xblock.wsgi import application
        logger.info("Starting Gunicorn server...")
        StandaloneApplication(application, options).run()

    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main() 