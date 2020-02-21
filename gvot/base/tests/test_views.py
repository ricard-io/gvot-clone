from django.urls import reverse

import pytest
from wagtail.core.models import Site

from ..models import SitePage
from .utils import count_text_in_content


@pytest.mark.django_db
class TestSitePage:
    def setup(self):
        assert SitePage.objects.count() == 1
        site = Site.objects.get(is_default_site=True)
        self.page_id = site.root_page.id
        self.data = {
            'title': "Titre de la page",
            'slug': 'testpage',
            'body': '[]',
            'body-count': 0,
        }

    def test_create_form(self, admin_client):
        url = reverse(
            'wagtailadmin_pages:add', args=['base', 'sitepage', self.page_id]
        )
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_create_and_publish(self, admin_client):
        url = reverse(
            'wagtailadmin_pages:add', args=['base', 'sitepage', self.page_id]
        )
        self.data['action-publish'] = True

        response = admin_client.post(url, self.data)
        assert response.status_code == 302
        assert SitePage.objects.count() == 2

    def test_display_published(self, admin_client):
        self.test_create_and_publish(admin_client)
        url = SitePage.objects.last().full_url

        response = admin_client.get(url)
        assert response.status_code == 200
        assert count_text_in_content(response, "Titre de la page")

    def test_preview(self, admin_client):
        url = reverse(
            'wagtailadmin_pages:preview_on_add',
            args=['base', 'sitepage', self.page_id],
        )
        response = admin_client.post(url, self.data)
        assert response.status_code == 200
        assert response.json().get('is_valid', False)

        response = admin_client.get(url)
        assert response.status_code == 200
        assert count_text_in_content(response, "Titre de la page")

        assert SitePage.objects.count() == 1
