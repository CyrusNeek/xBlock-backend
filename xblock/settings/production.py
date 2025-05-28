"""
Production settings for xblock project.
"""

import os
from pathlib import Path
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Get the Cloud Run service URL
CLOUD_RUN_SERVICE_URL = os.environ.get('CLOUD_RUN_SERVICE_URL', '')

# Update ALLOWED_HOSTS to include Cloud Run service URL and custom domains
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'api.brain.xblock.ai',
    'console.brain.xblock.ai',
    'brain.xblock.ai',
    CLOUD_RUN_SERVICE_URL,
    '.run.app',  # Allow all Cloud Run URLs
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CSRF_TRUSTED_ORIGINS = [
    "https://hub.xblock.ai",
    "https://app.xblock.ai",
    "https://admin.xblock.ai",
    "https://beta.xblock.ai",
    "https://stage.xblock.ai",
    "https://stage-front.xblock.ai",
    "https://console.brain.xblock.ai",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Admin site settings
ADMIN_URL = 'admin/'
FORCE_SCRIPT_NAME = ''  # Ensures admin is served at /admin/
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Trust the X-Forwarded-Proto header from Cloud Run
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Database configuration
import dj_database_url

# First try to use DATABASE_URL if provided
database_url = os.environ.get('DATABASE_URL')

# If no URL, construct database config from individual settings
if not database_url:
    database_url = (
        f"postgresql://"
        f"{os.environ.get('DATABASE_USER', '')}"
        f":{os.environ.get('DATABASE_PASSWORD', '')}"
        f"@{os.environ.get('DATABASE_HOST', '')}"
        f":{os.environ.get('DATABASE_PORT', '5432')}"
        f"/{os.environ.get('DATABASE_NAME', '')}"
    )

# Configure the database with health checks and SSL
DATABASES = {
    'default': dj_database_url.parse(
        database_url,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# Validate database configuration
required_db_settings = ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST', 'PORT']
for setting in required_db_settings:
    if setting not in DATABASES['default']:
        raise ValueError(f"Missing required database setting: {setting}")

# Static and Media files
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Use environment variables for paths
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

# Health check endpoint
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # 90%
    'MEMORY_MIN': 100,     # 100MB
}

# Gunicorn configuration is handled by entrypoint.sh
# Remove GUNICORN_CMD_ARGS to avoid conflicts
