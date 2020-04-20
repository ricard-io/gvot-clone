import csv

from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import Scrutin


class MaillingForm(forms.Form):
    """
    Formulaire pour les emaillings.
    """

    scrutin = forms.ModelChoiceField(
        queryset=Scrutin.objects,
        empty_label="Sélectionnez un scrutin",
        help_text="Les destinataires considérés seront ceux liés à ce scrutin.",
    )

    dests = forms.ChoiceField(
        choices=[
            (None, "Sélectionnez les destinataires"),
            ('tous', "Tous les participants"),
            ('exprimes', "Tous les participants ayant voté"),
            ('abstenus', "Tous les participants n'ayant pas encore voté"),
        ],
    )


class ImportForm(forms.Form):
    """
    Formulaire pour les imports CSV des pouvoirs.
    """

    scrutin = forms.ModelChoiceField(
        queryset=Scrutin.objects,
        empty_label="Sélectionnez un scrutin",
        help_text="Les pouvoirs importés ne seront associés qu'à ce scrutin.",
    )

    remplace = forms.BooleanField(
        label="Import hégémonique",
        help_text=(
            "Si coché, tous les pouvoirs existants lié au scrutin sélectionné "
            "seront détruits et/ou remplacés par l'importation."
        ),
        required=False,
    )

    csv_file = forms.FileField(
        help_text=mark_safe(
            "Fichier au format csv dans un codage utf-8 ; "
            "séparateur : « , » ; délimiteur de texte : « \" » (doubles "
            "quotes).<br>Colonnes attendues : « nom{star} », "
            "« prenom{star} », « collectif{star} », "
            "« courriel{star}{star} », « contact » et « ponderation ».<br>"
            "Au moins un colonne marquée par « {star} » doit être remplie.<br>"
            "Les colonnes marquée par « {star}{star} » ne peuvent être vides."
            "<br>Une pondération absente sera interprétée à la valeur « 1 »."
            .format(star='<span style="color:#cd3238">*</span>')
        ),
    )

    def clean_csv_file(self):
        csv_file = self.files['csv_file']
        csv_file.seek(0)  # rewind probably needed
        if csv_file.multiple_chunks():
            raise ValidationError(
                "Votre fichier est trop énorme. La limite est fixée à 2,5Mo."
            )
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
        except Exception as e:
            raise ValidationError(
                "Impossible de décoder votre fichier : {}".format(e)
            )
        try:
            reader = csv.reader(decoded_file)
            header = [s.strip() for s in reader.__next__()]
        except Exception:
            raise ValidationError(
                "Impossible de lire des données CSV dans ce fichier."
            )

        if not {'nom', 'prenom', 'courriel'}.issubset(set(header)):
            raise ValidationError(
                "Impossible de trouver les bonnes colonnes dans le fichier. "
                "Colonnes trouvées : {}.".format(
                    ", ".join(["« {} »".format(c) for c in header])
                )
            )
