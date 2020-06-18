from django import template

register = template.Library()


@register.filter
def pdb(value):
    import ipdb

    ipdb.set_trace()
    return value
