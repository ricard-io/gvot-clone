from . import env

"""
Django specific settings for GvoT project.
"""

# WAGTAIL
# ------------------------------------------------------------------------------
THIRD_PARTY_APPS = [
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.routable_page',
    'wagtailmenus',
    'tapeforms',
    'mailer',
    'docs',
]

WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (('footer', 'Menu de pied de page'),)

WAGTAILEMBEDS_FINDERS = [
    {'class': 'wagtail.embeds.finders.oembed'},
    {'class': 'wagtailembedpeertube.finders'},
]

# Since wagtail 2.7.4
WAGTAILFORMS_HELP_TEXT_ALLOW_HTML = True

# MISC
# ------------------------------------------------------------------------------
ASSISTANCE = env('ASSISTANCE', default='assistance@localhost')
