"""
WSGI config for xblock project.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# === EARLY ENVIRONMENT DUMP FOR CLOUD RUN DEBUGGING ===
logger.info("=== EARLY WSGI.PY ENV DUMP ===")
logger.info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
logger.info(f"DATABASE_NAME: {os.environ.get('DATABASE_NAME')}")
logger.info(f"DATABASE_USER: {os.environ.get('DATABASE_USER')}")
logger.info(f"DATABASE_PASSWORD: {'SET' if os.environ.get('DATABASE_PASSWORD') else 'NOT SET'}")
logger.info(f"DATABASE_HOST: {os.environ.get('DATABASE_HOST')}")
logger.info(f"DATABASE_PORT: {os.environ.get('DATABASE_PORT')}")
logger.info(f"SECRET_KEY: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")
logger.info(f"K_SERVICE: {os.environ.get('K_SERVICE')}")
logger.info(f"PORT: {os.environ.get('PORT')}")
logger.info("==============================")

# Load environment variables from BACKEND_ENV if running on Cloud Run
if os.environ.get("K_SERVICE") is not None:
    backend_env = os.environ.get("BACKEND_ENV")
    if backend_env:
        for line in backend_env.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())
else:
    try:
        import dotenv
        dotenv.load_dotenv()
        logger.info("Loaded .env for local development")
    except ImportError:
        logger.warning("python-dotenv not installed, skipping .env loading")

# Ensure DJANGO_SETTINGS_MODULE is set
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "xblock.settings.production"
    logger.info(f"Set DJANGO_SETTINGS_MODULE to {os.environ['DJANGO_SETTINGS_MODULE']}")

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logger.info("WSGI application loaded successfully")
except Exception as e:
    logger.error(f"Failed to load WSGI application: {str(e)}")
    raise

