"""
WSGI config for xblock project.
"""

import os
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
