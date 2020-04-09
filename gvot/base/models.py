import json
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls.converters import UUIDConverter

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractEmailForm,
    AbstractFormField,
    AbstractFormSubmission,
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.search import index

from . import blocks


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
    subpage_types = ['SitePage', 'ScrutinIndex']

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


class ScrutinIndex(Page):
    """
    Elle sert à lister les scrutins. Elle n'a a priori aucun intérêt à
    apparaître au public.
    """

    class Meta:
        verbose_name = "liste des scrutins"
        verbose_name_plural = "listes des scrutins"

    parent_page_types = ['SitePage', Page]
    subpage_types = ['Scrutin']

    @classmethod
    def can_create_at(cls, parent):
        # Seulement une instance possible
        return not cls.objects.exists() and super().can_create_at(parent)

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
        'Scrutin', on_delete=models.CASCADE, related_name='form_fields'
    )
    field_type = models.CharField(
        verbose_name='field type', max_length=16, choices=FORM_FIELD_CHOICES,
    )


class Vote(AbstractFormSubmission):
    pouvoir = models.ForeignKey('Pouvoir', on_delete=models.CASCADE)


# TODO: email d'annonce
# TODO: email de rappel
# TODO: email de confirmation
# TODO: afficher ouverture du scrutin dans la liste des scrutins
# TODO: une fois le scrutin ouvert et les votes enregistrés, fermer le
#       scrutin ne permet plus même de tester.
class Scrutin(RoutablePageMixin, AbstractEmailForm):
    """
    Elle sert à publier un scrutin pour une inscription à un évènement,
    une newsletter, etc. ou n'importe quelle récolte de données simples.
    """

    parent_page_types = ['ScrutinIndex']
    subpage_types = []

    ouvert = models.BooleanField(
        "Scrutin ouvert",
        default=False,
        blank=True,
        help_text="Tant que le scrutin n'est pas ouvert, il est fonctionnel "
        "pour les tests mais les votes ne sont pas enregistrés.",
    )

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

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        MultiFieldPanel(
            [
                FieldPanel('ouvert'),
                FieldPanel('peremption'),
                FieldPanel('prescription'),
            ], "Aspects RGPD",
        ),
        FieldPanel('introduction'),
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

    form_panels = [
        InlinePanel('form_fields', label="Champs de formulaire"),
    ]

    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Détails du scrutin"),
            ObjectList(form_panels, heading="Questionnaire"),
            ObjectList(promote_panels, heading="Promotion"),
            ObjectList(
                settings_panels, heading="Paramètres", classname='settings'
            ),
        ]
    )

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
    ]

    @route(r'^$')
    def no_way(self, request, *args, **kwargs):
        "Sauf en preview, le scrutin n'est pas accessible sans uuid valable"
        if request.is_preview:
            return super().serve(request, *args, **kwargs)
        raise Http404

    @route(r'(?P<uuid>' + UUIDConverter.regex + ')')
    def uuid_way(self, request, uuid, *args, **kwargs):
        pouvoir = get_object_or_404(Pouvoir, uuid=uuid)
        return pouvoir.scrutin.serve(request, *args, **kwargs)

    def serve(self, request, *args, **kwargs):
        _, _, path_args = self.resolve_subpage(request.path)
        pouvoir = get_object_or_404(Pouvoir, uuid=path_args['uuid'])

        if request.method == 'POST':
            form = self.get_form(
                request.POST, request.FILES, page=self, pouvoir=pouvoir
            )

            if form.is_valid():
                submission = self.process_form_submission(form, pouvoir)
                return self.render_landing_page(
                    request, submission, *args, **kwargs
                )
        else:
            form = self.get_form(pouvoir=pouvoir)

        context = self.get_context(request)
        context['form'] = form
        return render(request, self.get_template(request), context,)

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        pouvoir = kwargs.pop('pouvoir', None)
        vote = (
            self.get_submission_class()
            .objects.filter(pouvoir=pouvoir, page=self,)
            .first()
        )
        if vote:
            initial = json.loads(vote.form_data)
            return form_class(*args, initial=initial, **kwargs)
        return form_class(*args, **kwargs)

    def process_form_submission(self, form, pouvoir):
        if self.ouvert:
            self.get_submission_class().objects.update_or_create(
                pouvoir=pouvoir,
                page=self,
                defaults={
                    'form_data': json.dumps(
                        form.cleaned_data, cls=DjangoJSONEncoder
                    ),
                },
            )

    def get_submission_class(self):
        return Vote


class Pouvoir(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    scrutin = models.ForeignKey('Scrutin', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField('Prénom', max_length=100)
    courriel = models.EmailField()

    panels = [
        FieldPanel('scrutin'),
        MultiFieldPanel(
            [FieldRowPanel([FieldPanel('nom'), FieldPanel('prenom')])],
            "Identité",
        ),
        FieldPanel('courriel'),
    ]

    def __str__(self):
        return "{} {} ({})".format(self.prenom, self.nom, self.uuid)
