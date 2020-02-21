from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from .block_utils import (
    LinkMixin,
    TemplatedBlock,
    all_registered,
    register_block,
)

# Contenu texte
# ^^^^^^^^^^^^^


@register_block()
class Titre(TemplatedBlock):
    class Meta:
        icon = 'title'
        group = 'Contenu texte'

    niveau = blocks.ChoiceBlock(
        default='h2',
        choices=[
            ('h{}'.format(i), 'Titre de niveau {}'.format(i))
            for i in range(2, 7)
        ],
        icon='title',
    )
    texte = blocks.TextBlock(icon='pilcrow')


@register_block()
class Paragraphe(TemplatedBlock):
    class Meta:
        icon = 'pilcrow'
        group = 'Contenu texte'

    texte = blocks.RichTextBlock(icon='pilcrow')


@register_block()
class Bouton(LinkMixin, TemplatedBlock):
    class Meta:
        label = "Bouton"
        icon = 'link'
        group = 'Contenu texte'

    outline = blocks.BooleanBlock(
        label="Bordures colorées uniquement", required=False, default=False
    )

    texte = blocks.TextBlock(icon='pilcrow')

    lien = blocks.StreamBlock(
        LinkMixin.links_blocklist(),
        icon='link',
        help_text="Lien associé au bouton ; optionnel",
        required=False,
        max_num=1,
    )


# Contenu media
# ^^^^^^^^^^^^^


@register_block()
class Image(LinkMixin, TemplatedBlock):
    class Meta:
        icon = 'image'
        group = 'Contenu média'

    image = ImageChooserBlock(icon='image')

    legende = blocks.RichTextBlock(
        icon='pilcrow',
        label="légende",
        features=['ol', 'ul', 'bold', 'italic', 'link', 'document-link'],
        required=False,
    )

    lien = blocks.StreamBlock(
        LinkMixin.links_blocklist(),
        icon='link',
        help_text="Lien associé à l'image ; optionnel",
        required=False,
        max_num=1,
    )


@register_block()
class Embarque(TemplatedBlock):
    class Meta:
        icon = 'media'
        group = 'Contenu média'
        label = 'média embarqué'

    media = EmbedBlock(icon='link', help_text='Lien vers le média embarqué.')


# Contenu de page
# ^^^^^^^^^^^^^^^


def main_body_blocklist():
    return all_registered()
