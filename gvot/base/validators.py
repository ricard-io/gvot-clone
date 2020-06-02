from django.core.exceptions import ValidationError
from django.template import Context, Template


def validate_template(value):
    try:
        Template(value).render(Context({}))
    except Exception as e:
        raise ValidationError('Erreur au chargement du modèle : {}'.format(e))
