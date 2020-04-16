"""
Production settings.

- validate the configuration
- disable debug mode
- load secret key from environment variables
- set other production configurations
"""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa
from .base import TEMPLATES, env, var_dir

# CONFIGURATION VALIDATION
# ------------------------------------------------------------------------------
# Ensure that the database configuration has been set
if not env('DJANGO_DATABASE_URL', default=None):
    raise ImproperlyConfigured(
        "No database configuration has been set, you should check "
        "the value of your DATABASE_URL environment variable."
    )

# Ensure that the default email address has been set
if not env('DEFAULT_FROM_EMAIL', default=None):
    raise ImproperlyConfigured(
        "No default email address has been set, you should check "
        "the value of your DEFAULT_FROM_EMAIL environment variable."
    )

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#debug
DEBUG = False

# https://docs.djangoproject.com/en/stable/ref/settings/#secret-key
SECRET_KEY = env('DJANGO_SECRET_KEY')

# https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#templates
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
TEMPLATES[0]['OPTIONS']['loaders'] = [
    (
        'django.template.loaders.cached.Loader',
        [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ],
    )
]

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - %(module)s: %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': var_dir('log/gvot.log'),
            'formatter': 'verbose',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
        },
    },
    'loggers': {
        'django': {
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': True,
        },
        'django.request': {
            'level': 'WARNING',
            'handlers': ['file', 'mail_admins'],
            'propagate': True,
        },
        'gvot': {
            'level': 'INFO',
            'handlers': ['file', 'mail_admins'],
            'propagate': True,
        },
    },
}
if not os.path.isdir(var_dir('log')):
    os.mkdir(var_dir('log'), mode=0o750)

# ------------------------------------------------------------------------------
# APPLICATION AND 3RD PARTY LIBRARY SETTINGS
# ------------------------------------------------------------------------------

# MAILER
if not os.path.isdir(var_dir('lock')):
    os.mkdir(var_dir('lock'), mode=0o750)
