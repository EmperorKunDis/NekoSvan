from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Disable SECURE flags for local development (no HTTPS)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
