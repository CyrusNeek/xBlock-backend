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
    application = get_wsgi_application()
    from django.conf import settings
    assert settings.configured, "Settings not configured"
except Exception as e:
    raise RuntimeError("Django failed to load settings module!") from e
