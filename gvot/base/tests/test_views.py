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


@pytest.mark.django_db
class TestScrutinIndex:
    def test_get_should_fail(self, client, liste_scrutin):
        url = liste_scrutin.full_url
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestScrutin:
    def test_get_should_fail(self, client, scrutin):
        url = scrutin.full_url
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestPouvoir:
    def test_get_closed_scrutin(self, admin, client, pouvoir):
        pouvoir.scrutin.ouvert = False
        pouvoir.scrutin.save_revision(user=admin)
        pouvoir.scrutin.revisions.last().publish()

        url = '/{}'.format(pouvoir.uuid)
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert count_text_in_content(response, "Assemblée générale !")
        assert count_text_in_content(response, "Approbation du rapport")
        assert count_text_in_content(
            response, "<em>Oui</em> » ou « <em>Non</em>"
        )
        assert count_text_in_content(
            response,
            'value="Oui" required id="id_approbation-du-rapport_0" checked>',
        )
        assert count_text_in_content(
            response,
            'value="Non" required id="id_approbation-du-rapport_1">',
        )
        assert count_text_in_content(
            response, "Ce scrutin n'est pas encore ouvert."
        )

    def test_post_closed_scrutin(self, admin, client, pouvoir, mailoutbox):
        pouvoir.scrutin.ouvert = False
        pouvoir.scrutin.save_revision(user=admin)
        pouvoir.scrutin.revisions.last().publish()

        url = '/{}'.format(pouvoir.uuid)
        response = client.get(url, follow=True)
        assert response.status_code == 200

        url = response.redirect_chain[-1][0]
        response = client.post(url, data={'approbation-du-rapport': 'Non'})
        assert response.status_code == 200

        assert count_text_in_content(
            response, "Ce scrutin n'est pas encore ouvert."
        )
        assert count_text_in_content(response, "Assemblée générale !")
        assert not count_text_in_content(response, "Approbation du rapport")
        assert count_text_in_content(response, "Merci de votre participation.")
        assert count_text_in_content(response, "Retour à l'accueil")
        # ... et on a n'a pas de courriel.
        assert len(mailoutbox) == 0

        # Après le vote
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert count_text_in_content(response, "Assemblée générale !")
        assert count_text_in_content(response, "Approbation du rapport")
        assert count_text_in_content(
            response, "<em>Oui</em> » ou « <em>Non</em>"
        )
        assert count_text_in_content(
            response,
            'value="Oui" required id="id_approbation-du-rapport_0" checked>',
        )
        assert count_text_in_content(
            response,
            'value="Non" required id="id_approbation-du-rapport_1">',
        )
        assert count_text_in_content(
            response, "Ce scrutin n'est pas encore ouvert."
        )
        assert not count_text_in_content(
            response, "Merci de votre participation."
        )
        assert not count_text_in_content(response, "Retour à l'accueil")

    def test_get_scrutin(self, client, pouvoir):
        url = '/{}'.format(pouvoir.uuid)
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert count_text_in_content(response, "Assemblée générale !")
        assert count_text_in_content(response, "Approbation du rapport")
        assert count_text_in_content(
            response, "<em>Oui</em> » ou « <em>Non</em>"
        )
        assert count_text_in_content(
            response,
            'value="Oui" required id="id_approbation-du-rapport_0" checked>',
        )
        assert count_text_in_content(
            response,
            'value="Non" required id="id_approbation-du-rapport_1">',
        )

    def test_post_scrutin(self, client, pouvoir, mailoutbox):
        url = '/{}'.format(pouvoir.uuid)
        response = client.get(url, follow=True)
        assert response.status_code == 200

        url = response.redirect_chain[-1][0]
        response = client.post(url, data={'approbation-du-rapport': 'Non'})
        assert response.status_code == 200
        assert count_text_in_content(response, "Assemblée générale !")
        assert not count_text_in_content(response, "Approbation du rapport")
        assert count_text_in_content(response, "Merci de votre participation.")
        assert count_text_in_content(response, "Retour à l'accueil")

        # ... et on a un courriel.
        assert len(mailoutbox) == 1
        assert (
            "Confirmation de votre participation au scrutin « {} »".format(
                pouvoir.scrutin.title
            )
            == mailoutbox[0].subject
        )
        assert (
            "Nous avons bien enregistré votre vote pour le scrutin"
            in mailoutbox[0].body
        )

        # Après le vote
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert count_text_in_content(
            response, "Il semble que vous ayez déjà voté."
        )
        assert count_text_in_content(response, "Assemblée générale !")
        assert count_text_in_content(response, "Approbation du rapport")
        assert count_text_in_content(
            response, "<em>Oui</em> » ou « <em>Non</em>"
        )
        assert count_text_in_content(
            response,
            'value="Oui" required id="id_approbation-du-rapport_0">',
        )
        assert count_text_in_content(
            response,
            'value="Non" required id="id_approbation-du-rapport_1" checked>',
        )
