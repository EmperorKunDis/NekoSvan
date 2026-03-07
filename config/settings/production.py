"""Production settings for NekoSvan CRM."""

import os

from .base import *  # noqa: F401, F403

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "nekosvan"),
        "USER": os.environ.get("DB_USER", "nekosvan"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "https://praut.cz"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# CSRF
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS", "https://praut.cz,https://www.praut.cz"
).split(",")

# Static & Media
STATIC_URL = "/static/"
STATIC_ROOT = "/app/staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ONLYOFFICE
ONLYOFFICE_URL = os.environ.get("ONLYOFFICE_URL", "http://onlyoffice")
