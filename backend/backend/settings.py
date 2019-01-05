import environ
import os
import sys

from django.utils import timezone


root = environ.Path(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(os.path.join(root, 'apps'))

env = environ.Env(DEBUG=(bool, False))
env.read_env(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
SITE_ROOT = root()

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'users.backends.UserAuthentication',
)

# Application definition

INSTALLED_APPS = [
    'users',
    'dishes',
    'stoves',
    'rest_framework',
    'rest_framework.authtoken',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database

DATABASES = {
    'default': env.db(),
    'extra': env.db('SQLITE_URL', default='sqlite:////tmp/my-tmp-sqlite.db'),
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': f'django.contrib.auth.password_validation'
                f'.UserAttributeSimilarityValidator',
    },
    {
        'NAME': f'django.contrib.auth'
                f'.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': f'django.contrib.auth'
                f'.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': f'django.contrib.auth'
                f'.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

# Email confirmation setup
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
ENCODING_DES_KEY = 'ffffffff'

LOCAL_DOMAIN = 'http://localhost:8000'


# DRF AUTHENTICATION TOKEN CONSTANTS

USER_TOKEN_DURATION_DAYS = 1
USER_TOKEN_LIFETIME = timezone.timedelta(days=USER_TOKEN_DURATION_DAYS)

