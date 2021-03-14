import csv

from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import EmailTemplate, Scrutin


class MaillingForm(forms.Form):
    """
    Formulaire pour les emailings.
    """

    template = forms.ModelChoiceField(
        queryset=EmailTemplate.objects,
        empty_label="Sélectionnez un modèle",
    )

    dests = forms.ChoiceField(
        choices=[
            (None, "Sélectionnez les destinataires"),
            ('tous', "Tous les participants"),
            ('exprimes', "Tous les participants ayant voté"),
            ('abstenus', "Tous les participants n'ayant pas encore voté"),
        ],
    )

    filter_key = forms.ChoiceField(
        choices=(),
        required=False,
    )

    filter_ope = forms.ChoiceField(
        choices=(
            (None, "Choississez une opération de filtrage"),
            ('icontains', "Contient"),
            ('istartswith', "Commence par"),
            ('iendswith', "Termine par"),
            ('iexact', "Est"),
            ('not_isempty', "Est défini"),
            ('not_icontains', "Est défini et ne contient pas"),
            ('not_istartswith', "Est défini et ne commence pas par"),
            ('not_iendswith', "Est défini et ne termine pas par"),
            ('not_iexact', "Est défini et est différent de"),
            ('isempty', "N'est pas défini"),
            ('empty_not_icontains', "N'est pas défini ou ne contient pas"),
            (
                'empty_not_istartswith',
                "N'est pas défini ou ne commence pas par",
            ),
            ('empty_not_iendswith', "N'est pas défini ou ne termine pas par"),
            ('empty_not_iexact', "N'est pas défini ou est différent de"),
        ),
        required=False,
    )

    filter_val = forms.CharField(
        required=False,
        max_length=255,
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('filter_key') and not cleaned_data.get(
            'filter_ope'
        ):
            self.add_error(
                'filter_ope',
                ValidationError(
                    "Veuillez définir l'opération de filtrage à appliquer"
                ),
            )
        if cleaned_data.get('filter_ope') and not cleaned_data.get(
            'filter_key'
        ):
            self.add_error(
                'filter_key',
                ValidationError(
                    "Veuillez définir à quel champ s'applique le filtre"
                ),
            )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We dynamically override the choices to build a grouped select
        self.fields['template'].choices = [
            (None, self.fields['template'].empty_label)
        ] + [
            (
                scrutin.title,
                [
                    (tpl.id, "{} : {}".format(scrutin, tpl.nom))
                    for tpl in scrutin.emailtemplate_set.spammable()
                ],
            )
            for scrutin in Scrutin.objects.live().public()
        ]

        self.fields['filter_key'].choices = [
            (None, "Filtrez selon un champ personnalisé")
        ] + [
            (
                scrutin.title,
                [
                    (chp, "{} : {}".format(scrutin, chp))
                    for chp in scrutin.pouvoir_set.values_list(
                        'champ_perso__intitule', flat=True
                    ).distinct()
                ],
            )
            for scrutin in Scrutin.objects.live().public()
        ]


class MaillingSingleForm(forms.Form):
    """
    Formulaire pour renvoyer les infos d'un pouvoir.
    """

    def __init__(self, *args, pouvoir=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            'template'
        ].queryset = pouvoir.scrutin.emailtemplate_set.spammable()

    template = forms.ModelChoiceField(
        queryset=EmailTemplate.objects,
        empty_label="Sélectionnez un modèle",
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
            "<br>Une pondération absente sera interprétée à la valeur "
            "« 1 ».".format(star='<span style="color:#cd3238">*</span>')
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
