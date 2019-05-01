"""
Django settings for jaypark project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import socket
import sys

import boto3
from neomodel import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
def _is_local():
    return 'sinwoo' in socket.gethostname()


TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
DEBUG = not _is_local() and not TESTING

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3liy0^&fcl-(b%_l%h=)$o0)4(8lwqiy=5*3@r+$5!oyt$e4js'
if not TESTING:
    from jaypark.password import SECRET_KEY as IMPORTED_SECRET_KEY
    SECRET_KEY = IMPORTED_SECRET_KEY

ALLOWED_HOSTS = ['jaypark.sinwoobang.me']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'feed',
    'accounts',
    'post',
    'common',
    'storages'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jaypark.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'feed.context_processors.default_profile_photo_url',
                'feed.context_processors.datetimes',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jaypark.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {}
if TESTING:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
elif DEBUG or _is_local():
    from jaypark.password import DEBUG_DATABASE
    DATABASES = DEBUG_DATABASE
else:
    DATABASES['default'] = {}


# Graph
config.DATABASE_URL = 'bolt://jaypark:jay@graph@localhost:7687'  # default
if DEBUG:
    os.environ['NEOMODEL_CYPHER_DEBUG'] = '1'
if TESTING:  # for CI or Test
    config.DATABASE_URL = 'bolt://jayparktest:jay@graphtest@localhost:7687'


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]


# Accounts/Auth
LOGIN_REDIRECT_URL = '/feed/'
LOGOUT_REDIRECT_URL = '/feed/'
MAIN_REDIRECT_URL = '/feed/'

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true']
        },
    },
    'loggers': {
        'debugging': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    },
}

AUTH_USER_MODEL = 'accounts.User'


# Django Storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_QUERYSTRING_AUTH = False
S3_USE_SIGV4 = True
AWS_S3_USE_SSL = True
AWS_STORAGE_BUCKET_NAME = 'jaypark'
AWS_REGION = 'ap-northeast-2'
AWS_S3_HOST = 's3.%s.amazonaws.com' % AWS_REGION
AWS_DEFAULT_ACL = 'public-read'

credential = boto3.session.Session(profile_name='jaypark').get_credentials()
AWS_ACCESS_KEY_ID = credential.access_key
AWS_SECRET_ACCESS_KEY = credential.secret_key
