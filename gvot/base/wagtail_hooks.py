from django.urls import include, path, reverse
from django.utils.html import format_html

from wagtail.contrib.forms.wagtail_hooks import FormsMenuItem
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from . import admin_urls
from .models import Pouvoir
from .templatetags.minified import minified


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """Ajoute une feuille de styles personnalisée dans l'admin."""
    return format_html(
        '<link rel="stylesheet" href="{}">', minified('css/admin.css')
    )


class ImportButtonHelper(ButtonHelper):
    def import_button(self):
        classnames = ['bicolor', 'icon', 'icon-download']
        cn = self.finalise_classname(classnames)
        return {
            'url': reverse('import:index'),
            'label': 'Importer des %s' % self.verbose_name_plural,
            'classname': cn,
            'title': 'Importer des %s' % self.verbose_name_plural,
        }


@modeladmin_register
class PouvoirAdmin(ModelAdmin):
    model = Pouvoir
    menu_icon = 'group'
    menu_label = "Pouvoirs"
    list_display = ('uuid', 'prenom', 'nom', 'courriel', 'scrutin')
    list_filter = ('scrutin',)
    search_fields = ('prenom', 'nom', 'courriel')
    index_template_name = 'modeladmin/index_pouvoirs.html'
    button_helper_class = ImportButtonHelper


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('import-pouvoir/', include(admin_urls, namespace='import')),
    ]


@hooks.register('register_admin_menu_item')
def register_forms_menu_item():
    return FormsMenuItem(
        'Scrutins', reverse('wagtailforms:index'),
        name='scrutins', classnames='icon icon-form', order=700
    )


@hooks.register('construct_main_menu')
def hide_forms_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != 'forms']
