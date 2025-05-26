"""
WSGI config for xblock project.
"""

import os

# Load environment variables from .env file
import dotenv
# Note: 'os' module is assumed to be imported prior to this block (it is, just above).

# Path for .env file in Cloud Run
cloud_run_env_path = '/app/.env'

if os.path.exists(cloud_run_env_path):
    dotenv.load_dotenv(dotenv_path=cloud_run_env_path)
    print(f"DEBUG: Successfully loaded environment variables from {cloud_run_env_path}")
else:
    # Fallback for local development: try to find .env in the project structure
    # usecwd=True makes it search from the current working directory upwards.
    local_env_path = dotenv.find_dotenv(usecwd=True, raise_error_if_not_found=False)
    if local_env_path and os.path.exists(local_env_path):
        dotenv.load_dotenv(local_env_path)
        print(f"DEBUG: Successfully loaded environment variables from {local_env_path} (local fallback)")
    else:
        # This print is important as it indicates a potential configuration issue.
        print("DEBUG: .env file not found at /app/.env or locally. Proceeding without explicit .env loading by this script.")

from django.core.wsgi import get_wsgi_application

# Ensure DJANGO_SETTINGS_MODULE is set
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "xblock.settings.production"

# Initialize Django WSGI application
try:
    # Print current settings module for debugging
    print(f"Loading Django with settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    # Try to import the settings module directly first
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'xblock.settings.production')
    try:
        __import__(settings_module)
        print(f"Successfully imported {settings_module}")
    except ImportError as ie:
        print(f"Failed to import {settings_module}: {str(ie)}")
        raise
    
    # Now initialize the WSGI application
    application = get_wsgi_application()
    from django.conf import settings
    assert settings.configured, "Settings not configured"
    print("Django settings successfully configured")
    
except Exception as e:
    import traceback
    print(f"Error loading Django settings: {str(e)}")
    print("Traceback:")
    print(traceback.format_exc())
    raise RuntimeError("Django failed to load settings module!") from e
