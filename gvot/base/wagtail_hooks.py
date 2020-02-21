from django.utils.html import format_html

from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from wagtail.core import hooks

from .models import Pouvoir
from .templatetags.minified import minified


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """Ajoute une feuille de styles personnalisée dans l'admin."""
    return format_html(
        '<link rel="stylesheet" href="{}">', minified('css/admin.css')
    )


@modeladmin_register
class PouvoirAdmin(ModelAdmin):
    model = Pouvoir
    menu_icon = 'group'
    menu_label = "Pouvoirs"
    list_display = ('uuid', 'prenom', 'nom', 'courriel', 'scrutin')
    list_filter = ('scrutin',)
    search_fields = ('prenom', 'nom', 'courriel')
    # TODO: ajouter un import csv
