from django import template

register = template.Library()


@register.filter
def verbose_fieldname(model, field):
    """Raccourcis pour les titres des champs"""
    return model._meta.get_field(field).verbose_name


@register.filter(name="getattr")
def _getattr(obj, key):
    """Equivalent d'un getattr dans les templates."""
    return getattr(obj, key)


@register.filter
def get_champ_perso(obj, key):
    """Extrait un champs perso dans les templates."""
    champ_perso = obj.champ_perso.filter(intitule=key).first()
    return champ_perso.contenu if champ_perso else None


@register.filter(name="get")
def _get(obj, key):
    """Equivalent d'un get dans les templates."""
    return obj.get(key, "") if obj else None
