from django.urls import include, path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from wagtail.contrib.forms.wagtail_hooks import FormsMenuItem
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from . import import_urls, mailing_urls, scrutin_urls
from .models import EmailTemplate, Pouvoir
from .templatetags.minified import minified


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """Ajoute une feuille de styles personnalisée dans l'admin."""
    return format_html(
        '<link rel="stylesheet" href="{}">', minified('css/admin.css')
    )


class PouvoirButtonHelper(ButtonHelper):
    def import_button(self):
        classnames = ['bicolor', 'icon', 'icon-download']
        cn = self.finalise_classname(classnames)
        return {
            'url': reverse('import:index'),
            'label': 'Importer des %s' % self.verbose_name_plural,
            'classname': cn,
            'title': 'Importer des %s' % self.verbose_name_plural,
        }

    def mailing_button(self):
        classnames = ['bicolor', 'icon', 'icon-mail']
        cn = self.finalise_classname(classnames)
        return {
            'url': reverse('mailing:index'),
            'title': 'Démarrer un mailing',
            'label': 'Démarrer un mailing',
            'classname': cn,
        }

    def mail_button(self, pk):
        classnames = [
            'button',
            'button-small',
            'button-secondary',
            'icon',
            'icon-mail',
        ]
        cn = self.finalise_classname(classnames)
        return {
            'url': reverse('mailing:single', args=(pk,)),
            'title': 'Envoyer un email',
            'label': 'Envoyer un email',
            'classname': cn,
        }

    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        btns = super().get_buttons_for_obj(
            obj,
            exclude=exclude,
            classnames_add=classnames_add,
            classnames_exclude=classnames_exclude,
        )
        pk = getattr(obj, self.opts.pk.attname)
        btns.append(self.mail_button(pk))
        return btns


@modeladmin_register
class PouvoirAdmin(ModelAdmin):
    model = Pouvoir
    menu_icon = 'group'
    menu_label = "Pouvoirs"
    list_display = (
        'prenom',
        'nom',
        'courriels',
        'collectif',
        'scrutin',
        'ponderation',
        'champs_perso',
    )
    list_filter = ('scrutin',)
    search_fields = [
        'prenom',
        'nom',
        'collectif',
        'courriels__courriel',
        'champ_perso__contenu',
    ]
    index_template_name = 'modeladmin/index_pouvoirs.html'
    button_helper_class = PouvoirButtonHelper

    def courriels(self, obj):
        return mark_safe("<br>".join([str(c) for c in obj.courriels_list()]))

    courriels.short_description = "Courriel(s)"

    def champs_perso(self, obj):
        return mark_safe(
            "<dl class='inline-gvot'>{}</dl>".format(
                "".join(
                    [
                        format_html(
                            "<dt>{}</dt><dd>{}</dd>",
                            i,
                            c,
                        )
                        for i, c in obj.champ_perso.values_list(
                            'intitule', 'contenu'
                        )
                    ]
                )
            )
        )

    champs_perso.short_description = "Champs personnalisés"


@modeladmin_register
class EmailTemplateAdmin(ModelAdmin):
    model = EmailTemplate
    menu_icon = 'mail'
    menu_label = "Modèles de courriels"
    list_display = (
        'nom',
        'sujet',
        'scrutin',
    )
    list_filter = ('scrutin',)
    search_fields = ('nom', 'sujet', 'texte', 'html')


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('import-pouvoir/', include(import_urls, namespace='import')),
        path('mailing-pouvoir/', include(mailing_urls, namespace='mailing')),
        path('scrutin/', include(scrutin_urls, namespace='scrutin')),
    ]


@hooks.register('register_admin_menu_item')
def register_forms_menu_item():
    return FormsMenuItem(
        'Scrutins',
        reverse('wagtailforms:index'),
        name='scrutins',
        classnames='icon icon-form',
        order=700,
    )


@hooks.register('construct_main_menu')
def hide_forms_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != 'forms']
