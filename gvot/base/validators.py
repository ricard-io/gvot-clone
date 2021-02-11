import re

from django.core.exceptions import ValidationError
from django.template import Context, Template


def unescape_template_symbols(s):
    translation = {
        "&quot;": '"',
        "&#x27;": "'",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
    }
    regex = re.compile(r'({%[^(%})]+%})')
    r = ""
    for snippet in regex.split(s):
        if snippet.startswith('{%'):
            for entity, char in translation.items():
                snippet = snippet.replace(entity, char)
        r += snippet
    return r


def validate_template(value):
    try:
        Template(unescape_template_symbols(value)).render(Context({}))
    except Exception as e:
        raise ValidationError('Erreur au chargement du modèle : {}'.format(e))
