"""
WSGI config for xblock project.
"""

import os
import sys

# === EARLY ENVIRONMENT DUMP FOR CLOUD RUN DEBUGGING ===
print("=== EARLY WSGI.PY ENV DUMP ===", file=sys.stderr)
print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"), file=sys.stderr)
print("DATABASE_NAME:", os.environ.get("DATABASE_NAME"), file=sys.stderr)
print("DATABASE_USER:", os.environ.get("DATABASE_USER"), file=sys.stderr)
print("DATABASE_PASSWORD:", 'SET' if os.environ.get("DATABASE_PASSWORD") else 'NOT SET', file=sys.stderr)
print("DATABASE_HOST:", os.environ.get("DATABASE_HOST"), file=sys.stderr)
print("DATABASE_PORT:", os.environ.get("DATABASE_PORT"), file=sys.stderr)
print("SECRET_KEY:", 'SET' if os.environ.get("SECRET_KEY") else 'NOT SET', file=sys.stderr)
print("==============================", file=sys.stderr)

# Only load .env for local development (not on Cloud Run)
if os.environ.get("K_SERVICE") is None:
    try:
        import dotenv
        dotenv.load_dotenv()
        print("Loaded .env for local development", file=sys.stderr)
    except ImportError:
        pass


from django.core.wsgi import get_wsgi_application

# Ensure DJANGO_SETTINGS_MODULE is set
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "xblock.settings.production"


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

