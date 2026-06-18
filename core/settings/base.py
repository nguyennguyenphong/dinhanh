import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# Reading .env file
environ.Env.read_env(BASE_DIR / ".env")

# Secret key
# https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
SECRET_KEY = env("SECRET_KEY")

# Django settings
DEBUG = env.bool("DEBUG", default=False)

# Model
AUTH_USER_MODEL = "accounts.UserAccount"

# Allowed hosts
ALLOWED_HOSTS = ["*"]  # env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Installed apps
# https://docs.djangoproject.com/en/4.0/ref/applications/
INSTALLED_APPS = [
    # django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # third party
    "crispy_forms",
    "crispy_tailwind",
    "django_filters",
    "import_export",
    "corsheaders",
    "django_components",
    "compressor",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_vite",
    # apps
    "accounts",
    "branches",
    "dashboard",
    "menus",
    "system_config",
    "tenants",
    "feature_flags",
    "api_tokens",
    "media",
    "tags",
    "webhooks",
    "tasks",
    "comments",
    "routes",
    "vehicles",
    "hr",
    "trips",
    "customers_tickets",
    "payments",
    "consignments",
    "promotions_loyalty",
    "notifications",
    "financials",
    "assets",
    "reports",
]

# Middleware
# https://docs.djangoproject.com/en/4.0/topics/http/middleware/
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    #
    "core.middleware.CurrentUserMiddleware",
    #
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Root url
# https://docs.djangoproject.com/en/4.0/topics/http/urls/
ROOT_URLCONF = "core.urls"

# Templates
# https://docs.djangoproject.com/en/4.0/topics/templates/
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        # "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                "django_components.template_loader.Loader",
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    },
]

# WSGI
# https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
WSGI_APPLICATION = "core.wsgi.application"

# Authentication
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing/
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "vi"

# Timezone
# https://docs.djangoproject.com/en/4.0/topics/i18n/timezones/
TIME_ZONE = "Asia/Ho_Chi_Minh"

# i18n
# https://docs.djangoproject.com/en/4.0/ref/settings/#use-i18n
USE_I18N = True
USE_TZ = True

# Static files
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "/static/"

# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATICFILES_DIRS = [BASE_DIR / "static"]

# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
# https://docs.djangoproject.com/en/4.0/howto/static-files/
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "tenants" / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Crispy forms
# https://django-crispy-forms.readthedocs.io/en/latest/install.html
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# CORS
# https://github.com/adamchainz/django-cors-headers
CORS_ALLOW_ALL_ORIGINS = True

# Components
# https://django-components.readthedocs.io/en/latest/
COMPONENTS_NAMESPACE = "components"
COMPONENTS = {
    "autodiscover": True,
}

# Rest Framework
# https://www.django-rest-framework.org/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "burst": "60/minute",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Dinhanh API",
    "DESCRIPTION": "Bus Management System API",
    "VERSION": "1.0.0",
}

# Logging
# https://docs.djangoproject.com/en/4.0/topics/logging/
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "tenants": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}


# Cache
# https://docs.djangoproject.com/en/4.0/topics/cache/
# Development (local.py)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Cache timeout
CACHE_TIMEOUT = 300  # 5 minutes


# Mail
# https://docs.djangoproject.com/en/4.0/topics/email/
# Development (local.py)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery
# https://docs.celeryq.dev/en/stable/userguide/configuration.html
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Task queue configuration
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Retry configuration
CELERY_TASK_AUTORETRY_FOR = (Exception,)
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # 1 minute


# Cookie and Session
# https://docs.djangoproject.com/en/4.0/ref/settings/#session-cookie-secure
# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF configuration
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Cookie configuration
LANGUAGE_COOKIE_SECURE = True
LANGUAGE_COOKIE_HTTPONLY = True

# Django Vite
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_host": "localhost",
        "dev_server_port": 5173,
        "static_url_prefix": "" if DEBUG else "build/",
        "manifest_path": os.path.join(
            BASE_DIR, "static", "build", ".vite", "manifest.json"
        ),
    }
}

# 
AUTHENTICATION_BACKENDS = [
    # Default backend that allows authentication via USERNAME_FIELD (which we set to email)
    'django.contrib.auth.backends.ModelBackend',
]