"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from decouple import config
from kombu import Queue

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1&n7@(eq(f7j#4i5)ooud6jn+%8!f+@bo_y!rv^=ihv-ij&%&('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ["*"]
# alowed_host = config('ALLOWED_HOSTS')
# ALLOWED_HOSTS = alowed_host.split(',')

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'app.apps.AppConfig'
]

DATE_FORMAT = '%d-%m-%Y'

TIME_FORMAT = '%H:%M:%S'

DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'

DATE_INPUT_FORMATS = [
    '%d/%m/%Y',
    '%Y-%m-%d',
    '%d-%m-%Y',
    '%Y/%m/%d'
]

DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y/%m/%d %H:%M:%S',
    '%d-%m-%Y %H:%M:%S',
    '%d/%m/%Y %H:%M:%S'
] + DATE_INPUT_FORMATS


REST_FRAMEWORK = {
    'DATE_FORMAT': DATE_FORMAT,
    'DATETIME_FORMAT': DATETIME_FORMAT,
    'DATE_INPUT_FORMATS': DATE_INPUT_FORMATS,
    'DATETIME_INPUT_FORMATS': DATETIME_INPUT_FORMATS,
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated'
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',
    # ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.http.middlewares.logs_middleware.APILoggingMiddleware',
    'app.http.middlewares.authen_user_middleware.AuthenUserMiddleware',
    'app.http.middlewares.user_permission_middleware.UserPermissionMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('MYSQL_DATABASE_DB'),
        'USER': config('MYSQL_DATABASE_USER'),
        'PASSWORD': config('MYSQL_DATABASE_PASSWORD'),
        'HOST': config('MYSQL_DATABASE_HOST'),
        'PORT': config('MYSQL_DATABASE_PORT'),
        'POOL_OPTIONS': {
            'POOL_SIZE': 100,
            'MAX_OVERFLOW': 10,
            'RECYCLE': 500,
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST_CENTRALIZED = config("CENTRALIZED_SESSION_REDIS_HOST")
REDIS_PORT_CENTRALIZED = int(config("CENTRALIZED_SESSION_REDIS_PORT"))
REDIS_PASSWORD_CENTRALIZED = config("CENTRALIZED_SESSION_REDIS_PASSWORD")
REDIS_DATABASE_CENTRALIZED = int(config("CENTRALIZED_SESSION_REDIS_DATABASE"))
REDIS_HO_DATABASE_CENTRALIZED = int(config("CENTRALIZED_SESSION_REDIS_HO_DATABASE"))
REDIS_INFO_KPI_DATABASE_CENTRALIZED = int(config("CENTRALIZED_SESSION_REDIS_INFO_KPI_DATABASE"))


APP_ENVIRONMENT = config("APP_ENV")

CACHE_KEY_PREFIX = "job_services"

CACHE_VERSION = "v1"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST_CENTRALIZED}:{REDIS_PORT_CENTRALIZED}/0',
        'KEY_PREFIX': CACHE_KEY_PREFIX,
        'VERSION': CACHE_VERSION
    }
}

CELERY_BROKER_URL = f'redis://{REDIS_HOST_CENTRALIZED}:{REDIS_PORT_CENTRALIZED}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST_CENTRALIZED}:{REDIS_PORT_CENTRALIZED}/0'
CELERY_CACHE_BACKEND = "default"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = "Asia/Ho_Chi_Minh"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 3*60
# CELERY_RESULT_CACHE_MAX=5
CELERY_IMPORTS = ["app.http.tasks._tasks"]
CELERY_TASK_QUEUES = (
    Queue(f"{CACHE_KEY_PREFIX}__{CACHE_VERSION}"),
)
CELERY_TASK_DEFAULT_QUEUE = f"{CACHE_KEY_PREFIX}__{CACHE_VERSION}"
