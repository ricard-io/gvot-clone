import pytest

from .. import blocks


class TestBouton:
    def setup(self):
        self.block = blocks.Bouton()
        self.block.name = 'bouton'

    def test_bouton(self):
        data = {'outline': False, 'texte': "Bouton"}
        html = self.block.render(self.block.to_python(data))

        assert '<a class="btn btn-primary"' in html
        assert '</a>' in html
        assert "Bouton" in html

    def test_bouton_outline(self):
        data = {'outline': True, 'texte': "Bouton"}
        html = self.block.render(self.block.to_python(data))

        assert '<a class="btn btn-outline-primary"' in html
        assert '</a>' in html
        assert "Bouton" in html


@pytest.mark.django_db
class TestBoutonHref(TestBouton):
    def test_bouton_bad_page(self):
        data = {'texte': "Bouton", 'lien': [{'type': 'page', 'value': 42}]}
        html = self.block.render(self.block.to_python(data))

        assert 'href="#"' in html

    def test_bouton_page(self):
        data = {'texte': "Bouton", 'lien': [{'type': 'page', 'value': 3}]}
        html = self.block.render(self.block.to_python(data))

        assert 'href="/"' in html

    def test_bouton_image(self, image):
        data = {
            'texte': "Bouton",
            'lien': [{'type': 'image', 'value': image.id}],
        }
        html = self.block.render(self.block.to_python(data))

        assert 'href="{}"'.format(image.file.url) in html

    def test_bouton_document(self, document):
        data = {
            'texte': "Bouton",
            'lien': [{'type': 'document', 'value': document.id}],
        }
        html = self.block.render(self.block.to_python(data))

        assert 'href="{}"'.format(document.file.url) in html

    def test_bouton_externe(self):
        data = {
            'texte': "Bouton",
            'lien': [{'type': 'lien_externe', 'value': 'https://april.org'}],
        }
        html = self.block.render(self.block.to_python(data))

        assert 'href="https://april.org"' in html

    def test_bouton_ancre(self):
        data = {
            'texte': "Bouton",
            'lien': [{'type': 'ancre', 'value': '#blang'}],
        }
        html = self.block.render(self.block.to_python(data))

        assert 'href="#blang"' in html


class TestBoutonExcept(TestBouton):
    def test_get_context_pass(self):
        context = self.block.get_context({'lien': None})
        assert context['href'] == '#'

    def test_get_context_except(self, settings):
        settings.DEBUG = True
        with pytest.raises(Exception):
            self.block.get_context({'lien': True})


@pytest.mark.django_db
class TestImage:
    def setup(self):
        self.block = blocks.Image()
        self.block.name = 'image'

    def test_image(self, image):
        data = {'image': image.id}
        html = self.block.render(self.block.to_python(data))

        assert '<a' not in html
        assert '</a>' not in html
        assert 'figcaption' not in html
        assert 'alt="{}"'.format(image.title) in html
        assert (
            'src="{}"'.format(image.get_rendition('max-1200x1200').url) in html
        )

    def test_image_legende(self, image):
        data = {'image': image.id, 'legende': "Légende de l'image"}
        html = self.block.render(self.block.to_python(data))

        assert '<a' not in html
        assert '</a>' not in html
        assert 'figcaption' in html
        assert data['legende'] in html
        assert 'alt="{}"'.format(image.title) in html
        assert (
            'src="{}"'.format(image.get_rendition('max-1200x1200').url) in html
        )

    def test_image_bad_page(self, image):
        data = {'image': image.id, 'lien': [{'type': 'page', 'value': 42}]}
        html = self.block.render(self.block.to_python(data))

        assert '<a href="#"' in html

    def test_image_page(self, image):
        data = {'image': image.id, 'lien': [{'type': 'page', 'value': 3}]}
        html = self.block.render(self.block.to_python(data))

        assert '<a href="/"' in html

    def test_image_image(self, image):
        data = {
            'image': image.id,
            'lien': [{'type': 'image', 'value': image.id}],
        }
        html = self.block.render(self.block.to_python(data))

        assert '<a href="{}"'.format(image.file.url) in html

    def test_image_document(self, document, image):
        data = {
            'image': image.id,
            'lien': [{'type': 'document', 'value': document.id}],
        }
        html = self.block.render(self.block.to_python(data))

        assert '<a href="{}"'.format(document.file.url) in html

    def test_image_externe(self, image):
        data = {
            'image': image.id,
            'lien': [{'type': 'lien_externe', 'value': 'https://april.org'}],
        }
        html = self.block.render(self.block.to_python(data))

        assert '<a href="https://april.org"' in html

    def test_image_ancre(self, image):
        data = {
            'image': image.id,
            'lien': [{'type': 'ancre', 'value': '#blang'}],
        }
        html = self.block.render(self.block.to_python(data))

        assert '<a href="#blang"' in html


class TestParagraphe:
    def test_paragraphe(self):
        block = blocks.Paragraphe()
        block.name = 'paragraphe'

        data = {'texte': 'Texte du paragraphe'}
        html = block.render(block.to_python(data))

        assert data['texte'] in html


class TestTitre:
    def test_titre(self):
        block = blocks.Titre()
        block.name = 'titre'

        data = {'niveau': 'h3', 'texte': "Titre de niveau 3"}
        html = block.render(block.to_python(data))

        assert '<h3>' in html
        assert '</h3>' in html
        assert "Titre de niveau 3" in html
        assert '<a class="anchor" id="titre-de-niveau-3"' in html
