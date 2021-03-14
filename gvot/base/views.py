import csv

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView, detail

import dns.resolver
from wagtail.admin import messages

from . import forms, models


class ScrutinAdd(RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, *args, **kwargs):
        index = models.ScrutinIndex.objects.last()
        if not index:
            root = models.SitePage.objects.first()
            if not root:
                messages.error(
                    self.request,
                    "Impossible de trouver la racine de votre site.",
                )
                return reverse('wagtailadmin_home')
            messages.warning(
                self.request,
                "Impossible de trouver une page d'index des formulaires. "
                "Veillez d'abord en ajouter une.",
            )
            return reverse('wagtailadmin_pages:add_subpage', args=(root.id,))
        return reverse('wagtailadmin_pages:add_subpage', args=(index.id,))


class PouvoirUUIDMixin(detail.SingleObjectMixin):
    model = models.Pouvoir
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()


class RootUUID(PouvoirUUIDMixin, RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, *args, **kwargs):
        scrutin = self.object.scrutin
        return scrutin.url + scrutin.reverse_subpage(
            name='scrutin-uuid', args=(self.object.uuid,)
        )


class FormInvalidMixin:
    def form_invalid(self, form):
        messages.validation_error(self.request, self.get_error_message(), form)
        return self.render_to_response(self.get_context_data())


class MaillingSingle(FormInvalidMixin, PouvoirUUIDMixin, FormView):
    form_class = forms.MaillingSingleForm
    template_name = 'mailing/single.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pouvoir'] = self.object
        return kwargs

    def get_success_url(self):
        return reverse('mailing:single_confirm', args=(self.object.uuid,))

    def form_valid(self, form):
        # save data in session
        self.request.session['template_id'] = form.cleaned_data['template'].id
        return super().form_valid(form)

    def get_error_message(self):
        return "Le mailing n'a pas été poursuivi du fait d'erreurs."


class MaillingSingleConfirm(FormInvalidMixin, PouvoirUUIDMixin, FormView):
    form_class = forms.forms.Form
    template_name = 'mailing/single_confirm.html'
    success_url = reverse_lazy('base_pouvoir_modeladmin_index')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.template_id = self.request.session.get('template_id', None)

    def dispatch(self, request, *args, **kwargs):
        if (
            not models.EmailTemplate.objects.spammable()
            .filter(id=self.template_id)
            .exists()
        ):
            return redirect(
                reverse('mailing:single', args=(self.object.uuid,))
            )
        self.template = models.EmailTemplate.objects.get(id=self.template_id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.template.send_mail(self.request, self.object)
        messages.success(self.request, "Mailling démarré avec succès.")

        # drop now obsolete session data
        self.request.session.pop('template_id', False)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pouvoir'] = self.object
        context['scrutin'] = self.object.scrutin
        context['preview'] = dict(
            zip(
                ['subject', 'txt', 'html'],
                self.template.preview_mail(self.request, self.object),
            )
        )
        return context

    def get_error_message(self):
        return "L'envoi n'a pas été poursuivi du fait d'erreurs."


class MaillingIndex(FormInvalidMixin, FormView):
    form_class = forms.MaillingForm
    template_name = 'mailing/index.html'
    success_url = reverse_lazy('mailing:confirm')

    def form_valid(self, form):
        # save data in session
        self.request.session['dests'] = form.cleaned_data['dests']
        self.request.session['template_id'] = form.cleaned_data['template'].id
        self.request.session['filter_key'] = form.cleaned_data['filter_key']
        self.request.session['filter_ope'] = form.cleaned_data['filter_ope']
        self.request.session['filter_val'] = form.cleaned_data['filter_val']
        return super().form_valid(form)

    def get_error_message(self):
        return "Le mailing n'a pas été poursuivi du fait d'erreurs."


class MaillingConfirm(FormInvalidMixin, FormView):
    form_class = forms.forms.Form
    template_name = 'mailing/confirm.html'
    success_url = reverse_lazy('base_pouvoir_modeladmin_index')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.dests = self.request.session.get('dests', None)
        self.template_id = self.request.session.get('template_id', None)
        self.filter_key = self.request.session.get('filter_key', None)
        self.filter_ope = self.request.session.get('filter_ope', None)
        self.filter_val = self.request.session.get('filter_val', None)

    def dispatch(self, request, *args, **kwargs):
        if (
            not self.dests
            or not models.EmailTemplate.objects.spammable()
            .filter(id=self.template_id)
            .exists()
        ):
            return redirect(reverse('mailing:index'))
        self.template = models.EmailTemplate.objects.get(id=self.template_id)
        pouvoirs = self.template.scrutin.pouvoir_set.all()
        if self.dests == 'tous':
            self.qs = pouvoirs
        elif self.dests == 'exprimes':
            self.qs = pouvoirs.exclude(vote__isnull=True)
        elif self.dests == 'abstenus':
            self.qs = pouvoirs.filter(vote__isnull=True)

        if self.filter_key:
            if self.filter_ope in [
                'icontains',
                'iendswith',
                'iexact',
                'istartswith',
            ]:
                filtre = Q(champ_perso__intitule=self.filter_key) & Q(
                    **{
                        'champ_perso__contenu__'
                        + self.filter_ope: self.filter_val
                    }
                )
            elif self.filter_ope in [
                'not_icontains',
                'not_iendswith',
                'not_iexact',
                'not_istartswith',
            ]:
                filtre = Q(champ_perso__intitule=self.filter_key) & ~Q(
                    **{
                        'champ_perso__contenu__'
                        + self.filter_ope[4:]: self.filter_val
                    }
                )
            elif self.filter_ope in [
                'empty_not_icontains',
                'empty_not_iendswith',
                'empty_not_iexact',
                'empty_not_istartswith',
            ]:
                filtre = ~Q(champ_perso__intitule=self.filter_key) | (
                    Q(champ_perso__intitule=self.filter_key)
                    & ~Q(
                        **{
                            'champ_perso__contenu__'
                            + self.filter_ope[10:]: self.filter_val
                        }
                    )
                )
            elif self.filter_ope == 'isempty':
                filtre = ~Q(champ_perso__intitule=self.filter_key)
            elif self.filter_ope == 'not_isempty':
                filtre = Q(champ_perso__intitule=self.filter_key)

            self.qs = pouvoirs.filter(filtre).distinct()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        self.template.send_mailing(self.request, self.qs)
        messages.success(self.request, "Mailling démarré avec succès.")

        # drop now obsolete session data
        self.request.session.pop('dests', False)
        self.request.session.pop('template_id', False)
        self.request.session.pop('filter_key', False)
        self.request.session.pop('filter_ope', False)
        self.request.session.pop('filter_val', False)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scrutin'] = self.template.scrutin
        context['qs'] = self.qs
        context['nb_dests'] = self.qs.values_list(
            'courriels__courriel'
        ).count()
        if self.dests == 'tous':
            context['dests'] = "tous les participants"
        elif self.dests == 'exprimes':
            context['dests'] = "tous les participants ayant voté"
        elif self.dests == 'abstenus':
            context['dests'] = "tous les participants n'ayant pas encore voté"
        context['filter_key'] = self.filter_key
        context['filter_ope'] = (
            dict(forms.MaillingForm.declared_fields['filter_ope'].choices)
            .get(self.filter_ope)
            .lower()
        )
        context['filter_val'] = self.filter_val
        context['preview'] = dict(
            zip(
                ['subject', 'txt', 'html'],
                self.template.preview_mailing(self.request),
            )
        )
        return context

    def get_error_message(self):
        return "L'envoi n'a pas été poursuivi du fait d'erreurs."


class ImportIndex(FormInvalidMixin, FormView):
    form_class = forms.ImportForm
    template_name = 'import/index.html'
    success_url = reverse_lazy('import:confirm')

    def form_valid(self, form):
        # parse file
        csv_file = self.request.FILES.get('csv_file', None)
        csv_file.seek(0)  # rewind probably needed
        decoded_file = csv_file.read().decode('utf-8').splitlines()

        # save it in session
        self.request.session['csv_file'] = decoded_file
        self.request.session['scrutin_id'] = form.cleaned_data['scrutin'].id
        self.request.session['remplace'] = form.cleaned_data['remplace']

        # call success_url
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_multipart'] = True
        return context

    def get_error_message(self):
        return "L'import n'a pas été poursuivi du fait d'erreurs."


class ImportConfirm(FormInvalidMixin, FormView):
    form_class = forms.forms.Form
    template_name = 'import/confirm.html'
    success_url = reverse_lazy('base_pouvoir_modeladmin_index')

    champs_models = [
        'nom',
        'prenom',
        'collectif',
        'ponderation',
    ]
    champs_courriels = [
        'courriel',
    ]
    champs_persos = []

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.csv_file = self.request.session.get('csv_file', None)
        self.scrutin_id = self.request.session.get('scrutin_id', None)
        self.remplace = self.request.session.get('remplace', None)

    def dispatch(self, request, *args, **kwargs):
        if (
            not self.csv_file
            or not self.scrutin_id
            or not models.Scrutin.objects.filter(id=self.scrutin_id).exists()
        ):
            return redirect(reverse('import:index'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            return self.commit_csv_import(form)
        except Exception as e:
            if settings.DEBUG:
                raise e
            else:
                messages.error(
                    self.request,
                    "Impossible d'importer les pouvoirs. Une anomalie est "
                    "survenue : {}".format(e),
                )
                return super().form_invalid(form)

    def commit_csv_import(self, form):
        """Tout va bien, on importe."""
        ok, warn, ko = self.crible_data()
        if not ko:
            if self.remplace:
                models.Pouvoir.objects.filter(
                    scrutin_id=self.scrutin_id
                ).delete()

            created = models.Pouvoir.objects.bulk_create(
                [obj for _, obj, _ in ok + warn]
            )
            models.Courriel.objects.bulk_create(
                [
                    courriel
                    for pouvoir in created
                    for courriel in pouvoir.courriels.all()
                ]
            )

            if self.champs_persos:
                models.ChampPersonnalise.objects.bulk_create(
                    [
                        champ_perso
                        for pouvoir in created
                        for champ_perso in pouvoir.champ_perso.all()
                    ]
                )

            messages.success(self.request, "Pouvoirs importés avec succès.")

            # drop now obsolete session data
            self.request.session.pop('csv_file', False)
            self.request.session.pop('scrutin_id', False)
            self.request.session.pop('remplace', False)

            # call success_url
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def data_to_python(self):
        """Réifie les données en objets Python et les soumet à validation."""

        reader = csv.reader(self.csv_file)
        self.fieldnames = reader.__next__()
        self.champs_persos = [
            f
            for f in self.fieldnames
            if f not in self.champs_models + self.champs_courriels
        ]

        datas = [
            (
                {
                    k.strip(): v.strip() if isinstance(v, str) else v
                    for k, v in zip(self.fieldnames, r)
                    if isinstance(k, str) and k.strip() in self.champs_models
                },
                [
                    v.strip() if isinstance(v, str) else v
                    for k, v in zip(self.fieldnames, r)
                    if isinstance(k, str)
                    and k.strip() in self.champs_courriels
                    and v
                ],
                [
                    (k.strip(), v.strip() if isinstance(v, str) else v)
                    for k, v in zip(self.fieldnames, r)
                    if isinstance(k, str)
                    and k.strip()
                    not in self.champs_models + self.champs_courriels
                    and v
                ],
            )
            for r in reader
        ]

        # Par défaut on force les ponderation vides ou inexistantes à 1
        for data, _, _ in datas:
            data.update({'ponderation': data.get('ponderation', 1) or 1})

        return [
            models.Pouvoir(
                scrutin_id=self.scrutin_id,
                **model_data,
                courriels=[
                    models.Courriel(courriel=courriel)
                    for courriel in courriel_data
                ],
                champ_perso=[
                    models.ChampPersonnalise(
                        intitule=intitule, contenu=contenu
                    )
                    for intitule, contenu in other_data
                ]
            )
            for model_data, courriel_data, other_data in datas
        ]

    def check_objects_mx(self, object_list):
        domains = set(
            [c.split('@')[-1] for p in object_list for c in p.courriels_list()]
        )
        bad_mx_domains = {}
        for domain in domains:
            try:
                dns.resolver.query(domain, 'MX')
            except Exception as e:
                bad_mx_domains[domain] = str(e)
        return bad_mx_domains

    def crible_data(self):
        """Crible les lignes entre ce qu'on prend et ce qu'on rejette."""
        object_list = self.data_to_python()
        bad_mx_domains = self.check_objects_mx(object_list)
        ok, warn, ko = [], [], []

        # champs identifiants (doublons)
        id_fields = ('nom', 'prenom', 'collectif')

        courriels_in_db = (
            models.Pouvoir.objects.filter(scrutin_id=self.scrutin_id)
            .values_list('courriels__courriel')
            .distinct()
        )
        pouvoirs_in_db = models.Pouvoir.objects.filter(
            scrutin_id=self.scrutin_id
        ).values_list(*id_fields)

        courriels_in_import = set()
        pouvoirs_in_import = set()

        warnings_msg = [
            "Un pouvoir existe déjà {} avec {}.".format(lieu, force)
            for lieu in ["en base", "dans l'import"]
            for force in [
                "les mêmes attributs (doublon)",
                "cette adresse courriel",
            ]
        ]

        for index, obj in enumerate(object_list):
            try:
                # detect empty lines
                if (
                    not any(
                        (
                            getattr(obj, f)
                            for f in self.champs_models
                            if f != 'ponderation'
                        )
                    )
                    and not obj.courriels.exists()
                    and not obj.champ_perso.exists()
                ):
                    continue  # drop empty line

                # raise validation errors
                obj.full_clean()
                [
                    courriel.full_clean(exclude=['pouvoir'])
                    for courriel in obj.courriels.all()
                ]

                if any(
                    (
                        c.split('@')[-1] in bad_mx_domains
                        for c in obj.courriels_list()
                    )
                ):
                    bad_mx_msg = "Expédition impossible : domaine en erreur."
                    raise ValidationError({'courriel': bad_mx_msg})

                signature = tuple([getattr(obj, f) for f in id_fields])

                if not self.remplace and signature in pouvoirs_in_db:
                    warn.append((index, obj, warnings_msg[0]))
                elif not self.remplace and any(
                    (c in courriels_in_db for c in obj.courriels_list())
                ):
                    warn.append((index, obj, warnings_msg[1]))

                if signature in pouvoirs_in_import:
                    warn.append((index, obj, warnings_msg[2]))
                elif any(
                    (c in courriels_in_import for c in obj.courriels_list())
                ):
                    warn.append((index, obj, warnings_msg[3]))

                if not warn or warn[-1][0] != index:
                    ok.append((index, obj, None))
                    courriels_in_import = courriels_in_import.union(
                        set(obj.courriels_list())
                    )
                    pouvoirs_in_import.add(signature)
            except Exception as exception:
                ko.append((index, obj, exception))
        return ok, warn, ko

    def dry_run(self):
        """Crible les lignes en vue de l'affichage de la confirmation."""
        ok, warn, ko = self.crible_data()
        if ok and not warn and not ko:
            messages.success(
                self.request,
                "L'import est valide et peut être poursuivi.",
            )
        elif warn and not ko:
            messages.warning(
                self.request,
                "L'import est valide mais demande une attention "
                "particulière avant d'être poursuivi.",
            )
        elif ko:
            messages.error(
                self.request,
                "L'import ne peut être poursuivi du fait d'erreurs.",
                buttons=[
                    messages.button(
                        reverse('import:index'), "Re-tenter un import"
                    ),
                ],
            )
        return ok, warn, ko

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        (
            context['import_ok'],
            context['import_warn'],
            context['import_ko'],
        ) = self.dry_run()
        context['basic_fields'] = ['ligne'] + self.champs_models
        context['extended_fields'] = self.champs_persos
        context['model'] = models.Pouvoir
        return context

    def get_error_message(self):
        return "L'import n'a pas été poursuivi du fait d'erreurs."
