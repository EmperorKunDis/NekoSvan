import mimetypes

# Office document MIME types
mimetypes.add_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx", True)
mimetypes.add_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx", True)
mimetypes.add_type("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx", True)
mimetypes.add_type("application/msword", ".doc", True)
mimetypes.add_type("application/vnd.ms-excel", ".xls", True)
mimetypes.add_type("application/vnd.ms-powerpoint", ".ppt", True)
mimetypes.add_type("application/vnd.oasis.opendocument.text", ".odt", True)
mimetypes.add_type("application/vnd.oasis.opendocument.spreadsheet", ".ods", True)
mimetypes.add_type("application/vnd.oasis.opendocument.presentation", ".odp", True)

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Development-only fallback (production.py requires SECRET_KEY)
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-insecure-key-change-in-production",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Third-party
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "axes",
    # Local apps
    "src.accounts",
    "src.pipeline",
    "src.questionnaire",
    "src.pricing",
    "src.contracts",
    "src.projects",
    "src.notifications",
    "src.client_portal",
    "src.documents",
    "src.companies",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "nekosvan"),
        "USER": os.environ.get("DB_USER", "martinsvanda"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "cs"
TIME_ZONE = "Europe/Prague"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security: Cookie settings
# CSRF cookie must NOT be HttpOnly - JavaScript needs to read it for X-CSRFToken header
CSRF_COOKIE_HTTPONLY = False  # Keep False for SPA CSRF protection
CSRF_COOKIE_SECURE = True  # Only send over HTTPS in production
CSRF_COOKIE_SAMESITE = "Lax"  # CSRF protection via SameSite
SESSION_COOKIE_HTTPONLY = True  # Session cookie should be HttpOnly
SESSION_COOKIE_SECURE = True  # Only send over HTTPS in production
SESSION_COOKIE_SAMESITE = "Lax"

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
        "user": "120/minute",
        "portal_read": "30/minute",
        "portal_write": "10/minute",
    },
}

# Swagger/OpenAPI
SPECTACULAR_SETTINGS = {
    "TITLE": "NekoSvan API",
    "DESCRIPTION": "Workflow management system for ADNP, NekoSvan, Praut",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Django Cache (reuse Redis from Celery)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    }
}

# Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "check-overdue-payments": {
        "task": "src.contracts.tasks.check_overdue_payments",
        "schedule": 3600,  # Every hour
    },
    "check-inactive-deals": {
        "task": "src.pipeline.tasks.check_inactive_deals",
        "schedule": 3600,  # Every hour
    },
}

# N8N webhook base URL
N8N_WEBHOOK_BASE_URL = os.environ.get("N8N_WEBHOOK_BASE_URL", "http://localhost:5678/webhook")

# Client portal
CLIENT_PORTAL_BASE_URL = os.environ.get("CLIENT_PORTAL_BASE_URL", "http://localhost:4200/portal")

# ONLYOFFICE
ONLYOFFICE_URL = os.environ.get("ONLYOFFICE_URL", "http://localhost:9980")
ONLYOFFICE_JWT_SECRET = os.environ.get("ONLYOFFICE_JWT_SECRET", "")

# Ollama (local LLM for AI extraction)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

# Django Axes - Login Rate Limiting
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5  # Max 5 pokusů
AXES_COOLOFF_TIME = 0.25  # 15 minut lockout (0.25 hodiny)
AXES_LOCK_OUT_AT_FAILURE = True
AXES_ONLY_USER_FAILURES = False  # Track by IP
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = None  # API vrací JSON error
AXES_LOCKOUT_PARAMETERS = ["ip_address"]  # Lockout na IP
AXES_IPWARE_PROXY_COUNT = 1  # Support for reverse proxy (nginx)
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "HTTP_X_REAL_IP",
    "REMOTE_ADDR",
]
