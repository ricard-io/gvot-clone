from . import env

"""
Django specific settings for GvoT project.
"""

THIRD_PARTY_APPS = [
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.routable_page',
    'wagtailmenus',
    'widget_tweaks',
    'mailer',
]

WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (('footer', 'Menu de pied de page'),)

WAGTAILEMBEDS_FINDERS = [
    {'class': 'wagtail.embeds.finders.oembed'},
    {'class': 'wagtailembedpeertube.finders'},
]

ASSISTANCE = env('ASSISTANCE', default='assistance@localhost')
