"""
Django settings for GvoT project.

For more information on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/
"""
import os.path
from email.utils import getaddresses

from . import base_dir, env, root_dir
from .gvot import *
from .gvot import *

# ENVIRONMENT VARIABLES AND PATHS
# ------------------------------------------------------------------------------

# Local directory used for static and templates overrides
local_dir = base_dir.path('local')

# Directory for variable stuffs, i.e. user-uploaded media
var_dir = base_dir.path('var')
if not os.path.isdir(var_dir()):
    os.mkdir(var_dir(), mode=0o755)

# Location on which the application is served
APP_LOCATION = env('APP_LOCATION', default='/')

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', default=True)

# Local time zone for this installation
TIME_ZONE = 'Europe/Paris'

# https://docs.djangoproject.com/en/stable/ref/settings/#language-code
LANGUAGE_CODE = 'fr'

# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# https://docs.djangoproject.com/en/stable/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/stable/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/stable/ref/settings/#use-tz
USE_TZ = True

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# https://django-environ.readthedocs.io/en/stable/#supported-types
DATABASES = {
    'default': env.db(
        'DJANGO_DATABASE_URL',
        default='sqlite:///{}'.format(base_dir('sqlite.db')),
    )
}

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#root-urlconf
ROOT_URLCONF = 'gvot.urls'
# https://docs.djangoproject.com/en/stable/ref/settings/#wsgi-application
WSGI_APPLICATION = 'gvot.wsgi.application'

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

WAGTAIL_APPS = [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'modelcluster',
    'taggit',
]

# Project applications
LOCAL_APPS = ['gvot.base']

# https://docs.djangoproject.com/en/stable/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/stable/topics/auth/passwords/#using-argon2-with-django
    # 'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# https://docs.djangoproject.com/en/stable/topics/auth/passwords/#password-validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.MinimumLengthValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        )
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        )
    },
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#static-files
STATIC_ROOT = var_dir('static')

# https://docs.djangoproject.com/en/stable/ref/settings/#static-url
STATIC_URL = os.path.join(APP_LOCATION, 'static/')

# https://docs.djangoproject.com/en/stable/ref/settings/#staticfiles-dirs
STATICFILES_DIRS = [root_dir('static')]
if os.path.isdir(local_dir('static')):
    STATICFILES_DIRS.insert(0, local_dir('static'))

# https://docs.djangoproject.com/en/stable/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#media-root
MEDIA_ROOT = var_dir('media')

# https://docs.djangoproject.com/en/stable/ref/settings/#media-url
MEDIA_URL = os.path.join(APP_LOCATION, 'media/')

# https://docs.djangoproject.com/en/stable/ref/settings/#file-upload-directory-permissions
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
# https://docs.djangoproject.com/en/stable/ref/settings/#file-upload-permissions
FILE_UPLOAD_PERMISSIONS = 0o644

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [root_dir('templates')],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]
if os.path.isdir(local_dir('templates')):
    TEMPLATES[0]['DIRS'].insert(0, local_dir('templates'))

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#fixture-dirs
FIXTURE_DIRS = [root_dir('fixtures')]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/topics/email/#email-backends
# https://django-environ.readthedocs.io/en/stable/#supported-types
vars().update(env.email_url('DJANGO_EMAIL_URL', default='smtp://localhost:25'))

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
# Use the same email address for error messages
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ADMIN
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#admins
ADMINS = getaddresses([env('ADMINS', default='Cliss XXI <francois.poulain@cliss21.org>')])

# https://docs.djangoproject.com/en/stable/ref/settings/#managers
MANAGERS = ADMINS

# SESSIONS AND COOKIES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-path
SESSION_COOKIE_PATH = APP_LOCATION

# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-path
CSRF_COOKIE_PATH = APP_LOCATION

# WAGTAIL
# ------------------------------------------------------------------------------
# http://docs.wagtail.io/en/stable/advanced_topics/settings.html
WAGTAIL_SITE_NAME = "GvoT"

# Disable Gravatar provider
WAGTAIL_GRAVATAR_PROVIDER_URL = None

# Disable update checking on the dashboard
WAGTAIL_ENABLE_UPDATE_CHECK = False

# ------------------------------------------------------------------------------
# APPLICATION AND 3RD PARTY LIBRARY SETTINGS
# ------------------------------------------------------------------------------
