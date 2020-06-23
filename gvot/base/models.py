import json
import uuid

from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models import F, Q
from django.http import Http404, HttpResponseGone
from django.shortcuts import get_object_or_404, render
from django.template import Engine
from django.urls import reverse
from django.urls.converters import UUIDConverter
from django.utils import timezone

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
from wagtail.contrib.forms.forms import FormBuilder
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

from . import blocks, emails, validators
from .edit_handlers import AttendeesPanel, ResultsPanel
from .tapeforms import BigLabelTapeformMixin


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
] + [('lim_multiselect', 'Sélection multiple bornée')]


class FormField(AbstractFormField):
    """
    Classe des champs de formulaire.
    """

    page = ParentalKey(
        'Scrutin', on_delete=models.CASCADE, related_name='form_fields'
    )
    help_text = RichTextField(
        verbose_name="texte d'aide", blank=True, features=['bold', 'italic'],
    )
    field_type = models.CharField(
        verbose_name='field type', max_length=16, choices=FORM_FIELD_CHOICES,
    )
    min_values = models.PositiveSmallIntegerField(
        verbose_name='Valeurs min',
        null=True,
        blank=True,
        help_text="Nombre minimal de valeurs à choisir pour le champ de "
        "sélection multiple bornée",
    )
    max_values = models.PositiveSmallIntegerField(
        verbose_name='Valeurs max',
        null=True,
        blank=True,
        help_text="Nombre maximal de valeurs à choisir pour le champ de "
        "sélection multiple bornée",
    )
    panels = [
        FieldPanel('label'),
        FieldPanel('help_text'),
        FieldPanel('field_type', classname="formbuilder-type"),
        FieldPanel('choices', classname="formbuilder-choices"),
        FieldPanel('default_value', classname="formbuilder-default"),
        FieldRowPanel(
            [
                FieldPanel('required'),
                FieldPanel('min_values'),
                FieldPanel('max_values'),
            ]
        ),
    ]


class Vote(AbstractFormSubmission):
    pouvoir = models.ForeignKey('Pouvoir', on_delete=models.CASCADE)


class ClosedScrutin(Exception):
    pass


class LimitedSelectMultiple(forms.SelectMultiple):
    class Media:
        css = {'all': ('css/multi-select.css',)}
        js = ('js/multiselect.js', 'js/jquery.multi-select.js')

    def __init__(self, min_values, max_values, attrs={}, choices=()):
        attrs.update(
            {
                'class': 'limited-multiselect',
                'data-min': min_values,
                'data-max': max_values,
            }
        )
        super().__init__(attrs=attrs, choices=choices)


class MyFormBuilder(FormBuilder):
    def create_lim_multiselect_field(self, field, options):
        options['choices'] = map(
            lambda x: (x.strip(), x.strip()), field.choices.split(',')
        )
        validators = []
        if field.min_values:
            validators.append(MinLengthValidator(field.min_values))
        if field.max_values:
            validators.append(MaxLengthValidator(field.max_values))
        return forms.MultipleChoiceField(
            **options,
            validators=validators,
            widget=LimitedSelectMultiple(field.min_values, field.max_values)
        )


# TODO: afficher ouverture du scrutin dans la liste des scrutins
# FIXME: revoir le workflow ouvert / fermé ; c'est une mauvaise bidouille
# FIXME: ajouter un remerciement et une intro par défaut
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

    confirm_tpl = models.ForeignKey(
        'EmailTemplate',
        verbose_name='Modèle du courriel de confirmation',
        on_delete=models.SET_NULL,
        help_text="Par défaut il en sera fourni un à la création du scrutin. "
        "Si le champ est laissé vide, aucun courriel de confirmation ne sera "
        "envoyé.",
        null=True,
        blank=True,
        related_name='+',
    )

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        MultiFieldPanel(
            [
                FieldPanel('ouvert'),
                FieldPanel('peremption'),
                FieldPanel('prescription'),
            ],
            "Aspects RGPD",
        ),
        FieldPanel('introduction'),
        FieldPanel('confirmation'),
        MultiFieldPanel([FieldPanel('action')], "Appel à action"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [FieldPanel('from_address'), FieldPanel('to_address')]
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
    settings_panels = Page.settings_panels + [FieldPanel('confirm_tpl')]
    results_panels = [ResultsPanel()]
    attendees_panels = [AttendeesPanel()]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Détails du scrutin"),
            ObjectList(form_panels, heading="Questionnaire"),
            ObjectList(promote_panels, heading="Promotion"),
            ObjectList(
                settings_panels, heading="Paramètres", classname='settings'
            ),
            ObjectList(attendees_panels, heading="Émargements"),
            ObjectList(results_panels, heading="Résultats"),
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

    @route(r'(?P<uuid>' + UUIDConverter.regex + ')', name='scrutin-uuid')
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
                try:
                    submission = self.process_form_submission(
                        request, form, pouvoir
                    )
                    return self.render_landing_page(
                        request, submission, *args, **kwargs
                    )
                except ClosedScrutin:
                    return HttpResponseGone("Ce scrutin est fermé.")
        else:
            form = self.get_form(pouvoir=pouvoir)

        context = self.get_context(request)
        context['form'] = form
        context['deja_vote'] = (
            self.get_submission_class()
            .objects.filter(pouvoir=pouvoir, page=self)
            .exists()
        )
        return render(request, self.get_template(request), context)

    form_builder = MyFormBuilder

    def get_form_class(self):
        # Dynamically inherit Tapeform properties
        return type(
            'DynForm', (BigLabelTapeformMixin, super().get_form_class()), {}
        )

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        pouvoir = kwargs.pop('pouvoir', None)
        vote = (
            self.get_submission_class()
            .objects.filter(pouvoir=pouvoir, page=self)
            .first()
        )
        if vote:
            initial = json.loads(vote.form_data)
            return form_class(*args, initial=initial, **kwargs)
        return form_class(*args, **kwargs)

    def process_form_submission(self, request, form, pouvoir):
        # FIXME: documentation :
        # compte tenu que les types des questions/réponses ne sont pas
        # nécessairement multipliables, la seule façon de les comptabiliser
        # consiste à les dupliquer. Ce faisant la création ou la mise à jour
        # des soumissions est chamboulée.
        # FIXME: documentation et/ou à fixer
        # Il n'y a pas de verrouillage de la pondération au cours du vote.
        # Si ça devait bouger (ce qui serait tout de même une extraordinaire
        # mauvaise idée) on considère seule légitime la valeur initiale
        # s'il s'agit d'une MaJ du vote.
        if self.ouvert:
            form_data = json.dumps(form.cleaned_data, cls=DjangoJSONEncoder)
            votes = self.get_submission_class().objects.filter(pouvoir=pouvoir)
            if not votes:
                # Création
                votes.bulk_create(
                    pouvoir.ponderation
                    * [
                        votes.model(
                            pouvoir=pouvoir, page=self, form_data=form_data
                        )
                    ]
                )
            else:
                # Mise à jour
                votes.update(form_data=form_data, submit_time=timezone.now())
            pouvoir.notify_vote(request)

        elif not self.vote_set.exists():
            # Personne n'a oncore voté ; donc on est en test
            pass
        else:
            # Quelqu'un rejoue un POST alors que l'interface ne le propose pas
            raise ClosedScrutin

    def get_submission_class(self):
        return Vote

    def pondere(self):
        return self.pouvoir_set.exclude(ponderation=1).exists()

    def after_creation(self):
        # Create default scrutins's email templates
        tpl_engine = Engine.get_default()
        for base_tpl, nom in [
            ['confirmation_vote', "Confirmation du vote"],
            ['scrutin_ouvert', "Ouverture du scrutin"],
            ['rappel_code', "Rappel des codes"],
            ['envoit_resultats', "Envoit des résultats"],
        ]:
            sujet, texte, html = [
                tpl_engine.get_template(
                    "emails/{}.{}".format(base_tpl, suffix)
                ).source
                for suffix in ['subject', 'txt', 'html']
            ]
            tpl = self.emailtemplate_set.create(
                nom=nom, sujet=sujet, texte=texte, html=html
            )

            # Set default confirmation email template
            if base_tpl == 'confirmation_vote':
                self.confirm_tpl = tpl
                self.save()

    def context_values(self):
        return {
            **Scrutin.objects.filter(id=self.id).values()[0],
            'pondere': self.pondere(),
        }

    def pouvoir_context_values(self, qs):
        return [
            {
                **d,
                'uri': reverse('uuid', args=(d['uuid'],)),
                'scrutin': self.context_values(),
            }
            for d in qs.values()
        ]

    def results_distribution(self):
        votes = self.vote_set.all()

        compound_fields = self.get_data_fields()[1:]
        fields = [x[0] for x in compound_fields]
        headers = [x[1] for x in compound_fields]

        if not votes.exists():
            return {}
        m = [[json.loads(v.form_data)[f] for f in fields] for v in votes]

        # m as matrix. We transpose and transtype it to process
        results_grid = [
            [
                tuple(m[j][i]) if isinstance(m[j][i], list) else (m[j][i],)
                for j in range(len(m))
            ]
            for i in range(len(m[0]))
        ]

        # we flatten content
        flattened_results_grid = [
            [item for sublist in t for item in sublist] for t in results_grid
        ]

        distribution = [
            sorted(
                [(elem, line.count(elem)) for elem in set(line)],
                key=lambda x: x[1],
                reverse=True,
            )
            for line in flattened_results_grid
        ]

        return dict(zip(headers, distribution))


# FIXME: manque de manipulation en masse ? (suppression, compte)
class Pouvoir(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    scrutin = models.ForeignKey('Scrutin', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, null=True, blank=True)
    prenom = models.CharField('Prénom', max_length=100, null=True, blank=True)
    collectif = models.CharField(
        'Mandaire du collectif',
        max_length=100,
        null=True,
        blank=True,
        help_text="Le pouvoir doit au moins désigner un nom, "
        "un prénom ou un nom de collectif.",
    )
    courriel = models.EmailField()
    contact = models.CharField(
        "Contact alternatif en cas de courriel en erreur",
        max_length=100,
        null=True,
        blank=True,
    )
    ponderation = models.PositiveSmallIntegerField("Pondération", default=1,)

    panels = [
        FieldPanel('scrutin'),
        FieldPanel('ponderation'),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel('nom'), FieldPanel('prenom')]),
                FieldPanel('collectif'),
            ],
            "Identité",
        ),
        FieldPanel('courriel'),
        FieldPanel('contact'),
    ]

    def __str__(self):
        if self.collectif:
            return "{} ({})".format(self.collectif, self.uuid)
        if self.nom and self.prenom:
            return "{} {} ({})".format(self.prenom, self.nom, self.uuid)
        if self.nom or self.prenom:
            return "{} ({})".format(self.prenom or self.nom, self.uuid)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if not any([self.nom, self.prenom, self.collectif]):
            raise ValidationError(
                "Le pouvoir doit au moins désigner un nom, "
                "un prénom ou un nom de collectif."
            )

    def notify_vote(self, request):
        if self.scrutin.confirm_tpl:
            self.scrutin.confirm_tpl.send_mail(request, self)

    def context_values(self):
        qs = self._meta.model.objects.filter(pk=self.pk)
        return self.scrutin.pouvoir_context_values(qs)[0]


class EmailTemplateQuerySet(models.QuerySet):
    def spammable(self):
        # exclude confirmation templates
        return self.all().exclude(
            Q(id=F('scrutin__confirm_tpl__id')) & ~Q(scrutin__confirm_tpl=None)
        )


EmailTemplateManager = models.Manager.from_queryset(EmailTemplateQuerySet)


class EmailTemplate(models.Model):
    class Meta:
        verbose_name = "Modèle de courriel"
        verbose_name_plural = "Modèles de courriels"

    objects = EmailTemplateManager()

    scrutin = models.ForeignKey(
        'Scrutin',
        on_delete=models.CASCADE,
        help_text="Le scrutin concerné par ce modèle de courriel.",
    )
    nom = models.CharField(
        max_length=100, help_text="Utilisé uniquement comme repère interne."
    )
    sujet = models.CharField(
        "sujet du courriel",
        max_length=255,
        help_text="Le sujet du courriel. "
        "Peut inclure du balisage de gabarit Django. Voir la documentation.",
        validators=[validators.validate_template],
    )
    texte = models.TextField(
        "contenu du courriel, version texte",
        help_text="Peut inclure du balisage de gabarit Django."
        " Voir la documentation.",
        validators=[validators.validate_template],
    )
    html = RichTextField(
        "contenu du courriel, version HTML",
        help_text="Peut inclure du balisage de gabarit Django. "
        "Voir la documentation.",
        blank=True,
        features=[
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'bold',
            'italic',
            'ol',
            'ul',
            'hr',
            'link',
            'document-link',
        ],
        validators=[validators.validate_template],
    )

    panels = [
        FieldPanel('scrutin'),
        FieldPanel('nom'),
        MultiFieldPanel(
            [FieldPanel('sujet'), FieldPanel('texte'), FieldPanel('html')],
            "Détails du courriel",
        ),
    ]

    def __str__(self):
        return "{} ({}) - {}".format(self.nom, self.sujet, self.scrutin)

    def preview_mailing(self, request):
        context = {
            'pouvoir': {
                'uuid': uuid.uuid4(),
                'scrutin': self.scrutin.context_values(),
                'nom': request.user.last_name,
                'prenom': request.user.first_name,
                'courriel': request.user.email,
                'collectif': None,
                'contact': None,
                'ponderation': 1,
                'uri': reverse('uuid', args=(uuid.uuid4(),)),
            }
        }
        return emails.preview_templated(
            request, self, context, None, [request.user.email]
        )

    def send_mailing(self, request, qs):
        datas = [
            ({'pouvoir': d}, (d['courriel'],))
            for d in self.scrutin.pouvoir_context_values(qs)
        ]
        emails.send_mass_templated(request, self, None, datas)

    def preview_mail(self, request, pouvoir):
        context = {'pouvoir': pouvoir.context_values()}
        return emails.preview_templated(
            request, self, context, None, [pouvoir.courriel]
        )

    def send_mail(self, request, pouvoir):
        context = {'pouvoir': pouvoir.context_values()}
        emails.send_templated(request, self, context, None, [pouvoir.courriel])
