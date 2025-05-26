"""
WSGI config for xblock project.
"""

import os
import sys

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

