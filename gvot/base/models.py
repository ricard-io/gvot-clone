import uuid

from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls.converters import UUIDConverter

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractEmailForm,
    AbstractFormField,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.search import index

from . import blocks, mixins


class SitePage(Page):
    """
    La page générique de base du site web.
    """

    class Meta:
        verbose_name = "page standard"
        verbose_name_plural = "pages standard"

    # Contraintes de structure
    # ------------------------

    parent_page_types = ['SitePage', Page]
    subpage_types = ['SitePage', 'FormulaireIndex']

    # Contenu
    # -------

    body = StreamField(
        blocks.main_body_blocklist(),
        verbose_name="contenu",
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [StreamFieldPanel('body')]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]


class FormulaireIndex(mixins.UniqPage, Page):
    """
    Elle sert à lister les formulaires. Elle n'a a priori aucun intérêt à
    apparaître au public.
    """

    class Meta:
        verbose_name = "liste des formulaires"
        verbose_name_plural = "listes des formulaires"

    parent_page_types = ['SitePage', Page]
    subpage_types = ['Formulaire']

    def serve(self, request):
        raise Http404


# Override the field_type field with personnalized choices
FORM_FIELD_CHOICES = [
    (c[0], 'Choix multiples') if c[0] == 'checkboxes' else c
    for c in FORM_FIELD_CHOICES
    if c[0] not in ['datetime', 'hidden']
]


class FormField(AbstractFormField):
    """
    Classe des champs de formulaire.
    """

    page = ParentalKey(
        'Formulaire', on_delete=models.CASCADE, related_name='form_fields'
    )
    field_type = models.CharField(
        verbose_name='field type', max_length=16, choices=FORM_FIELD_CHOICES,
    )


# FIXME: s/Formulaire/Scrutin
class Formulaire(RoutablePageMixin, AbstractEmailForm):
    """
    Elle sert à publier un formulaire pour une inscription à un évènement,
    une newsletter, etc. ou n'importe quelle récolte de données simples.
    """

    parent_page_types = ['FormulaireIndex']
    subpage_types = []

    peremption = models.DateField(
        "Date de péremption",
        help_text="Uniquement destiné à avoir un point repère en vue de "
        "la suppression future des données",
    )
    prescription = RichTextField(
        default="Ces données sont recueillies dans le seul but "
        "décrit en introduction du formulaire. Les données "
        "recueillies dans le cadre de cette campagne ne seront pas "
        "utilisées à d’autres fins ni transmises à un tiers. Vous "
        "disposez d’un droit d’accès, de modification, de "
        "rectification et de suppression des données vous "
        "concernant (loi « Informatique et Liberté » du "
        "6 janvier 1978).",
        help_text="Texte destiné à avertir de l'utilisation qui sera faite "
        "des données recueillies.",
    )
    introduction = RichTextField(blank=True)
    action = models.TextField(
        default="Envoyer", help_text="Texte du bouton du formulaire.",
    )

    confirmation = RichTextField(blank=True)

    # FIXME: mettre les questions dans un panel séparé
    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        MultiFieldPanel(
            [
                FieldPanel('peremption'),
                FieldPanel('prescription'),
            ], "Aspects RGPD",
        ),
        FieldPanel('introduction'),
        InlinePanel('form_fields', label="Champs de formulaire"),
        FieldPanel('confirmation'),
        MultiFieldPanel(
            [
                FieldPanel('action'),
            ], "Appel à action"
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('from_address'),
                        FieldPanel('to_address'),
                    ]
                ),
                FieldPanel('subject'),
            ],
            "Envoi des résultats",
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
    ]

    @route(r'^$')
    def no_way(self, request, *args, **kwargs):
        "Le formulaire n'est pas accessible sans un uuid valable"
        raise Http404

    @route(r'(?P<uuid>'+ UUIDConverter.regex +')')
    def uuid_way(self, request, uuid, *args, **kwargs):
        pouvoir = get_object_or_404(Pouvoir, uuid=uuid)
        return pouvoir.scrutin.serve(request, *args, **kwargs)


class Pouvoir(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    scrutin = models.ForeignKey(Formulaire, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField('Prénom', max_length=100)
    courriel = models.EmailField()

    panels = [
        FieldPanel('scrutin'),
        FieldPanel('nom'),
        FieldPanel('prenom'),
        FieldPanel('courriel'),
    ]
