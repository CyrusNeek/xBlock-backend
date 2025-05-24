"""
WSGI config for xblock project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Allow Cloud Run secret-injected DJANGO_SETTINGS_MODULE to override
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "xblock.settings.production"

application = get_wsgi_application()

try:
    from django.conf import settings
    assert settings.configured
except Exception as e:
    raise RuntimeError("Django failed to load settings module!") from e
