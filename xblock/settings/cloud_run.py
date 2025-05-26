"""
Cloud Run specific settings for xblock project.
This is a simplified settings file specifically for Cloud Run deployment.
"""

import os
import logging
from xblock.settings.base import *  # Base settings

# ---------------------
# Core Configuration
# ---------------------
DEBUG = False

# Add Cloud Run URLs to allowed hosts
ALLOWED_HOSTS = [
    "api.brain.xblock.ai",
    "console.brain.xblock.ai",
    "brain.xblock.ai",
    "xblock-923738140935.us-central1.run.app",
    "*.run.app",  # Allow all Cloud Run URLs
    "localhost",
    "127.0.0.1",
]

# ---------------------
# Database Configuration
# ---------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', 'xblock'),
        'USER': os.environ.get('DATABASE_USER', 'xblock'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # 10 minutes connection persistence
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'prefer',
        },
    }
}

# ---------------------
# Static and Media Files
# ---------------------
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(BASE_DIR, 'staticfiles'))
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))

# ---------------------
# Enhanced Logging
# ---------------------
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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'xblock': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ---------------------
# Security Settings
# ---------------------
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False  # Handled by Cloud Run

# Strict Transport Security
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Extra headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# ---------------------
# Redis Configuration
# ---------------------
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CONSTANCE_REDIS_CONNECTION = REDIS_URL
