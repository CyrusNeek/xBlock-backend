"""
WSGI config for xblock project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Don't use setdefault here - we want to respect any existing settings module
# that's been set externally via environment variables
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'xblock.settings'

application = get_wsgi_application()
