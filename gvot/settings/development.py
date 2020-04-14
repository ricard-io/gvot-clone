"""
Development settings.

- use Console backend for emails sending by default
- add the django-debug-toolbar
"""
from .base import *  # noqa
from .base import INSTALLED_APPS, MIDDLEWARE, env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#secret-key
SECRET_KEY = env('DJANGO_SECRET_KEY', default='CHANGEME!!!')

# https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list(
    'DJANGO_ALLOWED_HOSTS', default=['localhost', '0.0.0.0', '127.0.0.1']
)

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/topics/email/#email-backends
# https://django-environ.readthedocs.io/en/stable/#supported-types
vars().update(env.email_url('DJANGO_EMAIL_URL', default='consolemail://'))
MAILER_EMAIL_BACKEND = EMAIL_BACKEND  # noqa
EMAIL_BACKEND = 'mailer.backend.DbBackend'

# WAGTAIL
# ------------------------------------------------------------------------------
# http://docs.wagtail.io/en/stable/contributing/styleguide.html
INSTALLED_APPS += ['wagtail.contrib.styleguide']

# ------------------------------------------------------------------------------
# APPLICATION AND 3RD PARTY LIBRARY SETTINGS
# ------------------------------------------------------------------------------

# DJANGO DEBUG TOOLBAR
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/stable/installation.html
if env.bool('DJANGO_DEBUG_TOOLBAR', default=False):
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INSTALLED_APPS += ['debug_toolbar']
    INTERNAL_IPS = ['127.0.0.1']
    DEBUG_TOOLBAR_CONFIG = {
        'DISABLE_PANELS': ['debug_toolbar.panels.redirects.RedirectsPanel'],
        'SHOW_TEMPLATE_CONTEXT': True,
    }

# DJANGO EXTENSIONS
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/stable/index.html
INSTALLED_APPS += ['django_extensions']
