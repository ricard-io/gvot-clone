from django.test.html import parse_html


def parse_content(response, html=False):
    """
    Décode et retourne le contenu de la réponse, en le transformant en
    objet de structure Python si `html` vaut `True`.
    """
    if (
        hasattr(response, "render")
        and callable(response.render)
        and not response.is_rendered
    ):
        response.render()
    content = response.content.decode(response.charset)
    return parse_html(content) if html else content


def count_text_in_content(response, text, html=False):
    """
    Retourne le nombre d'occurrence de `text` dans le contenu de la réponse,
    en les analysant en tant que HTML si `html` vaut `True`.

    Cette méthode se base sur `django.test.SimpleTestCase.assertContains()`,
    et pourrait être remplacée après l'intégration de pytest-django#709.
    """
    content = parse_content(response, html=html)
    text = parse_html(text) if html else str(text)
    return content.count(text)
