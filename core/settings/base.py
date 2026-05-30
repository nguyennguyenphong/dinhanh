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
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Installed apps
# https://docs.djangoproject.com/en/4.0/ref/applications/
INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'crispy_forms',
    'crispy_tailwind',
    'django_filters',
    'import_export',
    'corsheaders',

    # apps
    'accounts',
    'branches',
    'dashboard',
    'menus',
    'system_config',
    'tenants',
    'feature_flags',
    'api_tokens',
    'media',
    'tags',
    'webhooks',
    'tasks',
    'comments',
    'routes',
    'vehicles',
    'hr',
    'trips',
    'customers_tickets',
    'payments',
    'consignments',
    'promotions_loyalty',
    'notifications',
    'financials',
    'assets',
    'reports',
]

# Middleware
# https://docs.djangoproject.com/en/4.0/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root url
# https://docs.djangoproject.com/en/4.0/topics/http/urls/
ROOT_URLCONF = 'core.urls'

# Templates
# https://docs.djangoproject.com/en/4.0/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
# https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
WSGI_APPLICATION = 'core.wsgi.application'

# Authentication
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing/
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'vi'

# Timezone
# https://docs.djangoproject.com/en/4.0/topics/i18n/timezones/
TIME_ZONE = 'Asia/Ho_Chi_Minh'

# i18n
# https://docs.djangoproject.com/en/4.0/ref/settings/#use-i18n
USE_I18N = True
USE_TZ = True

# Static files
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = '/static/'

# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
# https://docs.djangoproject.com/en/4.0/howto/static-files/
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy forms
# https://django-crispy-forms.readthedocs.io/en/latest/install.html
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# CORS
# https://github.com/adamchainz/django-cors-headers
CORS_ALLOW_ALL_ORIGINS = True