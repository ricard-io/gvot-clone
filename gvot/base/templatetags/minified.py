import functools
import os.path

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@functools.lru_cache(maxsize=None)
def get_minified_static_path(path):
    """Retourne de préférence le chemin d'un fichier compressé.

    Détermine et retourne le chemin relatif à utiliser pour le fichier
    statique `path`, en fonction de l'environnement. Si elle existe, la
    version compressée (e.g. avec le suffixe `.min` avant l'extension) du
    fichier sera retournée quand le débogage est désactivé.
    """
    if settings.DEBUG:
        return path
    root, ext = os.path.splitext(path)
    min_path = '{}.min{}'.format(root, ext or '')
    if finders.find(min_path):
        return min_path
    return path


@register.simple_tag
def minified(path):
    """Retourne le chemin absolu d'un fichier statique compressé."""
    return static(get_minified_static_path(path))
