"""
Production settings for xblock project.
"""

import os
from ..settings import *  # Base settings

# ---------------------
# 🔒 Core Security Config
# ---------------------

# NEVER allow True as default
DEBUG = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = [
    "api.brain.xblock.ai",
    "console.brain.xblock.ai",
    "brain.xblock.ai",
    "xblock-923738140935.us-central1.run.app",
    # Add more production domains here if needed
]

# ---------------------
# 🔐 Production Security Settings
# ---------------------
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Strict Transport Security
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Extra headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# ---------------------
# 🧼 Disable dev utilities
# ---------------------
# DO NOT import debug_server or anything printing envs here

# ---------------------
# 📌 Extra production configs (optional)
# ---------------------
# LOGGING = {...}
# DATABASES override if needed
