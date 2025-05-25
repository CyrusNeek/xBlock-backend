"""
WSGI config for xblock project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Ensure DJANGO_SETTINGS_MODULE is set
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "xblock.settings.production"

# Print settings module for debugging
print(f"Using Django settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

# Initialize Django WSGI application
try:
    application = get_wsgi_application()
    # Verify settings are loaded
    from django.conf import settings
    print(f"Settings loaded successfully. DEBUG={settings.DEBUG}")
    assert settings.configured, "Settings not configured"
except Exception as e:
    import traceback
    print("Failed to load Django settings:")
    print(traceback.format_exc())
    raise RuntimeError("Django failed to load settings module!") from e
