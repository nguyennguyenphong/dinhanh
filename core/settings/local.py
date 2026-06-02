from .base import *
import environ

env = environ.Env()

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "django_extensions",
    "django_browser_reload",
]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

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
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

# 
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True
