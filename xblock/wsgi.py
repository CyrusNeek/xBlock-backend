"""
WSGI config for xblock project.
"""
import os
import sys
import logging

# --- Configure Logging Early ---
# Ensure logging is configured before any log messages are attempted.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)] # Log to stderr for Cloud Run
)
logger = logging.getLogger(__name__) # Use a specific logger for this module

logger.info("--- WSGI.PY SCRIPT STARTED ---")

# --- Log Initial Environment State (Key Variables) ---
logger.info("--- Initial Environment Variables (Partial Dump) ---")
logger.info(f"DJANGO_SETTINGS_MODULE (initial): {os.environ.get('DJANGO_SETTINGS_MODULE')}")
logger.info(f"SECRET_KEY (initial): {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")
logger.info(f"DATABASE_NAME (initial): {os.environ.get('DATABASE_NAME')}")
logger.info(f"BACKEND_ENV variable (initial): {'SET' if os.environ.get('BACKEND_ENV') else 'NOT SET'}")
if os.environ.get('BACKEND_ENV'):
    logger.info(f"BACKEND_ENV content (first 100 chars): {os.environ.get('BACKEND_ENV', '')[:100]}")
logger.info(f"K_SERVICE (Cloud Run service name): {os.environ.get('K_SERVICE')}")
logger.info("--- End of Initial Environment Variables ---")


# --- Environment Variable Loading Logic ---
# This section handles loading variables from BACKEND_ENV if present,
# or from a .env file for local development.

# Flag to track if BACKEND_ENV was processed
backend_env_processed = False

if os.environ.get("K_SERVICE") is not None: # Indicates running on Cloud Run
    logger.info("Running on Cloud Run (K_SERVICE is set).")
    backend_env_content = os.environ.get("BACKEND_ENV")

    if backend_env_content:
        logger.info("BACKEND_ENV variable is set. Attempting to parse it.")
        lines_parsed = 0
        keys_loaded_from_backend_env = []
        for line in backend_env_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # setdefault ensures we don't overwrite if Cloud Run already expanded it
                    # from the secret manager (envFrom behavior)
                    if key not in os.environ:
                        os.environ[key] = value
                        logger.info(f"Loaded from BACKEND_ENV: {key} (newly set)")
                    else:
                        logger.info(f"Loaded from BACKEND_ENV: {key} (already existed, not overwritten by BACKEND_ENV parsing)")
                    keys_loaded_from_backend_env.append(key)
                    lines_parsed += 1
                except ValueError:
                    logger.warning(f"Could not parse line from BACKEND_ENV: '{line}'")
        logger.info(f"Finished parsing BACKEND_ENV. Parsed {lines_parsed} lines. Keys attempted: {keys_loaded_from_backend_env}")
        backend_env_processed = True
    else:
        logger.info("Running on Cloud Run, but BACKEND_ENV variable is NOT set or is empty. "
                    "Assuming environment variables are set directly by Cloud Run (e.g., via 'envFrom' secret).")
else: # Not running on Cloud Run (likely local development)
    logger.info("Not running on Cloud Run (K_SERVICE is not set). Attempting to load .env file for local development.")
    try:
        import dotenv
        # Construct path to .env file in the project root (assuming wsgi.py is in a subdirectory like 'xblock')
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(project_root, '.env')
        if os.path.exists(dotenv_path):
            dotenv.load_dotenv(dotenv_path=dotenv_path, override=True) # Override allows .env to take precedence locally
            logger.info(f"Successfully loaded .env file from: {dotenv_path}")
        else:
            logger.warning(f".env file not found at: {dotenv_path}")
    except ImportError:
        logger.warning("python-dotenv library not installed. Skipping .env file loading.")
    except Exception as e:
        logger.error(f"Error loading .env file: {e}", exc_info=True)

# --- Log Environment State After Potential Modifications ---
logger.info("--- Environment Variables After Processing (Partial Dump) ---")
logger.info(f"DJANGO_SETTINGS_MODULE (after processing): {os.environ.get('DJANGO_SETTINGS_MODULE')}")
logger.info(f"SECRET_KEY (after processing): {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")
logger.info(f"DATABASE_NAME (after processing): {os.environ.get('DATABASE_NAME')}")
logger.info("--- End of Environment Variables After Processing ---")

# --- Django Application Setup ---
from django.core.wsgi import get_wsgi_application

logger.info("Attempting to get Django WSGI application (this will trigger django.setup())...")
try:
    application = get_wsgi_application()
    logger.info("Successfully got Django WSGI application. Django setup complete.")
except Exception as e:
    logger.error(f"CRITICAL ERROR DURING DJANGO SETUP (get_wsgi_application): {e}", exc_info=True)
    # If Django setup fails, re-raise the exception to prevent Gunicorn from starting a broken worker
    raise

logger.info("--- WSGI.PY SCRIPT COMPLETED SUCCESSFULLY ---")

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

