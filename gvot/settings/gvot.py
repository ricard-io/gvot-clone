"""
Django specific settings for GvoT project.
"""

THIRD_PARTY_APPS = [
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.routable_page',
    'wagtailmenus',
    'widget_tweaks',
]

WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (('footer', 'Menu de pied de page'),)

WAGTAILEMBEDS_FINDERS = [
    {'class': 'wagtail.embeds.finders.oembed'},
    {'class': 'wagtailembedpeertube.finders'},
]
