from django.conf import settings
from django.utils.text import camel_case_to_spaces, slugify

from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock

# Mixins
########


class TemplatedBlock(blocks.StructBlock):
    def get_template(self, *args, **kwargs):
        return "blocks/{}.html".format(slugify(self.name))


class LinkMixin:
    def links_blocklist():
        return [
            ('page', blocks.PageChooserBlock(target_model='base.SitePage')),
            ('document', DocumentChooserBlock()),
            ('image', ImageChooserBlock()),
            (
                'lien_externe',
                blocks.URLBlock(
                    icon='link', help_text="Lien vers un site externe."
                ),
            ),
            (
                'ancre',
                blocks.TextBlock(
                    icon='fa fa-anchor',
                    help_text="Ancre dans la page. Ex : #infos",
                ),
            ),
        ]

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        lien = value['lien']
        context['href'] = None
        try:
            if lien:
                if hasattr(lien[0].value, 'file') and hasattr(
                    lien[0].value.file, 'url'
                ):
                    context['href'] = lien[0].value.file.url
                elif hasattr(lien[0].value, 'url'):
                    context['href'] = lien[0].value.url
                else:
                    context['href'] = lien[0].value
        except Exception as e:
            if settings.DEBUG:
                raise e
        if not context['href']:
            context['href'] = '#'
        return context


# Management
############


REGISTERED_BLOCKS = {}


def register_block():
    """
    Macro hygiénique pour conserver une liste des blocs décrits,
    groupés par type.
    """

    class Wrapper:
        def __init__(self, cls, *args, **kwargs):
            self.wrapped = cls(*args, **kwargs)
            title = camel_case_to_spaces(cls.__name__).replace(' ', '_')
            group = cls._meta_class.group
            if group not in REGISTERED_BLOCKS:
                REGISTERED_BLOCKS[group] = []
            REGISTERED_BLOCKS[group].append((title, cls))

        def __call__(self, *args, **kwargs):
            return self.wrapped

    return Wrapper


def all_registered():
    return [
        (name, bloc())
        for group in REGISTERED_BLOCKS
        for name, bloc in REGISTERED_BLOCKS[group]
    ]
