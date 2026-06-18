import environ

from .base import *

env = environ.Env()

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ["*"]

LOGIN_URL = "http://127.0.0.1:8001/accounts/login/"

INSTALLED_APPS += [
    "django_extensions",
    "django_browser_reload",
]

MIDDLEWARE.insert(1, "django_browser_reload.middleware.BrowserReloadMiddleware")

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME", default="dinhanh_db"),
        "USER": env("DATABASE_USER", default="dinhanh_user"),
        "PASSWORD": env("DATABASE_PASSWORD", default="T+75yTa_Z(wj"),
        "HOST": env("DATABASE_HOST", default="localhost"),
        "PORT": env("DATABASE_PORT", default="5432"),
        # Performance settings
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "connect_timeout": 10,
        },
        # Connection pooling
        "ATOMIC_REQUESTS": False,
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

#
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True


#

COMPRESS_ROOT = BASE_DIR / "static"

COMPRESS_ENABLED = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]
