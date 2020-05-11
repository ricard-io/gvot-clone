from django import template

import ipdb

register = template.Library()


@register.filter
def pdb(value):
    ipdb.set_trace()
    return value
