"""
Production settings for xblock project.
"""

from .base import *

# Override any base settings here for production

# For security in production
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [
    "api.brain.xblock.ai",
    "console.brain.xblock.ai",
    "brain.xblock.ai",
    "xblock-923738140935.us-central1.run.app",
    # Add any other production domains here
]

# Security settings for production
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Add any other production-specific settings here
