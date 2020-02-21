from django.template import Context, Template

import pytest

from ..templatetags.minified import get_minified_static_path


@pytest.fixture
def mock_static_find(monkeypatch):
    def find(*args, **kwargs):
        return True

    # patch pour trouver n'importe quel fichier dans les statics
    monkeypatch.setattr('django.contrib.staticfiles.finders.find', find)


class TestMinified:
    def setup(self):
        # vide le cache avant chaque test
        get_minified_static_path.cache_clear()

    def test_get_path_debug(self, mock_static_find, settings):
        settings.DEBUG = True
        assert get_minified_static_path('test/debug.css') == 'test/debug.css'

    @pytest.mark.parametrize(
        'path, result',
        [
            ('test/app.css', 'test/app.min.css'),
            ('test/no_extension', 'test/no_extension.min'),
        ],
    )
    def test_get_path_exists(self, mock_static_find, path, result):
        assert get_minified_static_path(path) == result

    def test_get_path_not_found(self):
        assert get_minified_static_path('unknown.txt') == 'unknown.txt'

    def test_tag(self, mock_static_find, settings):
        rendered = Template(
            '{% load minified %}{% minified "test/tag.css" %}'
        ).render(Context())
        assert rendered == settings.STATIC_URL + 'test/tag.min.css'
