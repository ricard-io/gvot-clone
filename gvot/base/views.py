import csv

from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView, detail

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

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        self.template.send_mailing(self.request, self.qs)
        messages.success(self.request, "Mailling démarré avec succès.")

        # drop now obsolete session data
        self.request.session.pop('dests', False)
        self.request.session.pop('template_id', False)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scrutin'] = self.template.scrutin
        context['nb'] = self.qs.count()
        if self.dests == 'tous':
            context['dests'] = "tous les participants"
        elif self.dests == 'exprimes':
            context['dests'] = "tous les participants ayant voté"
        elif self.dests == 'abstenus':
            context['dests'] = "tous les participants n'ayant pas encore voté"
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

    champs = [
        'nom',
        'prenom',
        'collectif',
        'courriel',
        'contact',
        'ponderation',
    ]

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
        return self.commit_csv_import(form)

    def commit_csv_import(self, form):
        """Tout va bien, on importe."""
        ok, warn, ko = self.crible_data()
        if not ko:
            if self.remplace:
                models.Pouvoir.objects.filter(
                    scrutin_id=self.scrutin_id
                ).delete()

            models.Pouvoir.objects.bulk_create(
                [obj for _, obj, _ in ok + warn]
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

        reader = csv.DictReader(self.csv_file)

        datas = [
            (
                {
                    k.strip(): v.strip() if isinstance(v, str) else v
                    for k, v in r.items()
                    if isinstance(k, str) and k.strip() in self.champs
                },
                [
                    (k.strip(), v.strip() if isinstance(v, str) else v)
                    for k, v in r.items()
                    if isinstance(k, str) and k.strip() not in self.champs
                ],
            )
            for r in reader
        ]

        # Par défaut on force les ponderation vides ou inexistantes à 1
        for data, _ in datas:
            data.update({'ponderation': data.get('ponderation', 1) or 1})

        return (
            models.Pouvoir(
                scrutin_id=self.scrutin_id,
                **model_data,
                champ_perso=[
                    models.ChampPersonnalise(
                        intitule=intitule, contenu=contenu
                    )
                    for intitule, contenu in other_data
                ]
            )
            for model_data, other_data in datas
        )

    def crible_data(self):
        """Crible les lignes entre ce qu'on prend et ce qu'on rejette."""
        object_list = self.data_to_python()
        ok, warn, ko = [], [], []

        # champs identifiants (doublons)
        id_fields = ('nom', 'prenom', 'collectif', 'courriel')

        courriels_in_db = models.Pouvoir.objects.filter(
            scrutin_id=self.scrutin_id
        ).values_list('courriel')
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
                if not any(
                    [
                        getattr(obj, f)
                        for f in self.champs
                        if f != 'ponderation'
                    ]
                ):
                    continue  # drop empty line

                obj.full_clean()

                signature = tuple([getattr(obj, f) for f in id_fields])

                if not self.remplace and signature in pouvoirs_in_db:
                    warn.append((index, obj, warnings_msg[0]))
                elif not self.remplace and (obj.courriel,) in courriels_in_db:
                    warn.append((index, obj, warnings_msg[1]))

                if signature in pouvoirs_in_import:
                    warn.append((index, obj, warnings_msg[2]))
                elif (obj.courriel,) in courriels_in_import:
                    warn.append((index, obj, warnings_msg[3]))

                if not warn or warn[-1][0] != index:
                    ok.append((index, obj, None))
                    courriels_in_import.add((obj.courriel,))
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
        context['import_fields'] = ['ligne'] + self.champs
        context['model'] = models.Pouvoir
        return context

    def get_error_message(self):
        return "L'import n'a pas été poursuivi du fait d'erreurs."
