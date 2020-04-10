import csv

from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from wagtail.admin import messages

from . import forms, models


class ImportIndex(FormView):
    form_class = forms.ImportForm
    template_name = 'import/index.html'
    success_url = reverse_lazy('import:confirm')

    def form_valid(self, form):
        return self.confirm_csv_import(form)

    def confirm_csv_import(self, form):
        # drop previous hypothetic session data
        self.request.session.pop('csv_file', None)
        self.request.session.pop('scrutin', None)
        self.request.session.pop('remplace', None)

        # parse file
        csv_file = self.request.FILES.get('csv_file', None)
        csv_file.seek(0)  # rewind probably needed
        decoded_file = csv_file.read().decode('utf-8').splitlines()

        # save it in session
        self.request.session['csv_file'] = decoded_file
        self.request.session['scrutin'] = form.cleaned_data['scrutin'].id
        self.request.session['remplace'] = form.cleaned_data['remplace']

        # call success_url
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_multipart'] = True
        return context

    def get_error_message(self):
        return "L'import n'a pas été poursuivi du fait d'erreurs."

    def form_invalid(self, form):
        messages.validation_error(self.request, self.get_error_message(), form)
        return self.render_to_response(self.get_context_data())


class ImportConfirm(FormView):
    form_class = forms.forms.Form
    template_name = 'import/confirm.html'
    success_url = reverse_lazy('base_pouvoir_modeladmin_index')

    champs = ['nom', 'prenom', 'courriel', 'contact', 'ponderation']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.csv_file = self.request.session.get('csv_file', None)
        self.scrutin = self.request.session.get('scrutin', None)
        self.remplace = self.request.session.get('remplace', None)

    def dispatch(self, request, *args, **kwargs):
        if not self.csv_file or not self.scrutin:
            return redirect(reverse('import:index'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        return self.commit_csv_import(form)

    def commit_csv_import(self, form):
        """Tout va bien, on importe."""
        ok, warn, ko = self.crible_data()
        if not ko:
            if self.remplace:
                models.Pouvoir.objects.filter(scrutin_id=self.scrutin).delete()

            models.Pouvoir.objects.bulk_create([obj for _, obj, _ in ok + warn])
            messages.success(self.request, "Pouvoirs importés avec succès.")

            # drop now obsolete session data
            self.request.session.pop('csv_file', False)
            self.request.session.pop('scrutin', False)
            self.request.session.pop('remplace', False)

            # call success_url
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def data_to_python(self):
        """Réifie les données en objets Python et les soumet à validation."""

        reader = csv.DictReader(self.csv_file)

        datas = [
            {
                k.strip(): v.strip()
                for k, v in r.items()
                if k.strip() in self.champs
            }
            for r in reader
        ]

        # Par défaut on force les ponderation vides à 1
        [d.update({"ponderation": d["ponderation"] or 1}) for d in datas]

        return (models.Pouvoir(scrutin_id=self.scrutin, **d) for d in datas)

    def crible_data(self):
        """Crible les lignes entre ce qu'on prend et ce qu'on rejette."""
        object_list = self.data_to_python()
        ok, warn, ko = [], [], []

        courriels_in_db = models.Pouvoir.objects.filter(
            scrutin_id=self.scrutin
        ).values_list('courriel')
        pouvoirs_in_db = models.Pouvoir.objects.filter(
            scrutin_id=self.scrutin
        ).values_list(*self.champs)

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
                obj.full_clean()

                if (
                    not self.remplace
                    and (obj.nom, obj.prenom, obj.courriel) in pouvoirs_in_db
                ):
                    warn.append((index, obj, warnings_msg[0]))
                elif not self.remplace and (obj.courriel,) in courriels_in_db:
                    warn.append((index, obj, warnings_msg[1]))

                if (obj.nom, obj.prenom, obj.courriel,) in courriels_in_import:
                    warn.append((index, obj, warnings_msg[2]))
                elif (obj.courriel,) in courriels_in_import:
                    warn.append((index, obj, warnings_msg[3]))

                if not warn or warn[-1][0] != index:
                    ok.append((index, obj, None))
                    courriels_in_import.add((obj.courriel,))
                    pouvoirs_in_import.add((obj.nom, obj.prenom, obj.courriel))
            except Exception as exception:
                ko.append((index, obj, exception))
        return ok, warn, ko

    def dry_run(self):
        """Crible les lignes en vue de l'affichage de la confirmation."""
        ok, warn, ko = self.crible_data()
        if ok and not warn and not ko:
            messages.success(
                self.request, "L'import est valide et peut être poursuivi.",
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

    def form_invalid(self, form):
        messages.validation_error(self.request, self.get_error_message(), form)
        return self.render_to_response(self.get_context_data())
