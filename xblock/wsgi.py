"""
WSGI config for xblock project.
"""

import os
import sys

# Load environment variables from .env file
import dotenv
# Note: 'os' and 'sys' modules are imported above.

# Path for .env file in Cloud Run
cloud_run_env_path = '/app/.env'

print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE before dotenv: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)

if os.path.exists(cloud_run_env_path):
    dotenv.load_dotenv(dotenv_path=cloud_run_env_path)
    print(f"DEBUG WSGI.PY: Attempted to load environment variables from {cloud_run_env_path}", file=sys.stderr)
    print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE after dotenv load from {cloud_run_env_path}: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
    print(f"DEBUG WSGI.PY: DATABASE_URL from env after load: {os.environ.get('DATABASE_URL')}", file=sys.stderr)
    print(f"DEBUG WSGI.PY: SECRET_KEY from env after load: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}", file=sys.stderr)
else:
    # Fallback for local development
    local_env_path = dotenv.find_dotenv(usecwd=True, raise_error_if_not_found=False)
    if local_env_path and os.path.exists(local_env_path):
        dotenv.load_dotenv(local_env_path)
        print(f"DEBUG WSGI.PY: Attempted to load environment variables from {local_env_path} (local fallback)", file=sys.stderr)
        print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE after dotenv load from {local_env_path}: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
        print(f"DEBUG WSGI.PY: DATABASE_URL from env after local load: {os.environ.get('DATABASE_URL')}", file=sys.stderr)
        print(f"DEBUG WSGI.PY: SECRET_KEY from env after local load: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}", file=sys.stderr)
    else:
        print("DEBUG WSGI.PY: .env file not found at /app/.env or locally. Proceeding without explicit .env loading by this script.", file=sys.stderr)

print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE after entire dotenv block: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)

from django.core.wsgi import get_wsgi_application

# Ensure DJANGO_SETTINGS_MODULE is set
print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE before conditional set: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE not in os.environ, setting to xblock.settings.production", file=sys.stderr)
    os.environ["DJANGO_SETTINGS_MODULE"] = "xblock.settings.production"
else:
    print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE already in os.environ: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
print(f"DEBUG WSGI.PY: DJANGO_SETTINGS_MODULE after conditional set block: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)

# Initialize Django WSGI application
try:
    # Print current settings module for debugging
    print(f"DEBUG WSGI.PY: Loading Django with settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)
    
    # Try to import the settings module directly first
    settings_module_path = os.environ.get('DJANGO_SETTINGS_MODULE') # Rely on it being set
    if not settings_module_path:
        print("DEBUG WSGI.PY: CRITICAL - DJANGO_SETTINGS_MODULE is not set before trying to import it!", file=sys.stderr)
        raise ValueError("DJANGO_SETTINGS_MODULE is not set")
    
    print(f"DEBUG WSGI.PY: Attempting to import settings module: {settings_module_path}", file=sys.stderr)
    try:
        __import__(settings_module_path)
        print(f"DEBUG WSGI.PY: Successfully imported {settings_module_path}", file=sys.stderr)
    except ImportError as ie:
        print(f"DEBUG WSGI.PY: Failed to import {settings_module_path}: {str(ie)}", file=sys.stderr)
        # Print PYTHONPATH for more context on import errors
        print(f"DEBUG WSGI.PY: PYTHONPATH: {os.environ.get('PYTHONPATH')}", file=sys.stderr)
        print(f"DEBUG WSGI.PY: sys.path: {sys.path}", file=sys.stderr)
        raise
    
    # Now initialize the WSGI application
    print("DEBUG WSGI.PY: Calling get_wsgi_application()", file=sys.stderr)
    application = get_wsgi_application()
    print("DEBUG WSGI.PY: get_wsgi_application() returned", file=sys.stderr)
    
    # Verify settings are configured
    from django.conf import settings
    if settings.configured:
        print("DEBUG WSGI.PY: Django settings successfully configured (settings.configured is True)", file=sys.stderr)
    else:
        print("DEBUG WSGI.PY: WARNING - Django settings NOT configured (settings.configured is False)", file=sys.stderr)
        # Attempt to trigger settings configuration if not already done by get_wsgi_application
        # This is unusual to need here, but as a diagnostic.
        # django.setup() # Usually called by get_wsgi_application or manage.py

except Exception as e:
    import traceback
    print(f"DEBUG WSGI.PY: Error during Django WSGI app initialization: {str(e)}", file=sys.stderr)
    print("DEBUG WSGI.PY: Traceback:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    # Ensure the original error type is preserved if possible, or use a generic one
    # The original code raises RuntimeError, which might mask the actual underlying issue like ImproperlyConfigured
    # However, for Cloud Run, a clear signal that the app failed is important.
    raise # Re-raise the original exception to let it propagate
