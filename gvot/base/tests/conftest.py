import datetime

from django.contrib.auth.models import User

import pytest
from wagtail.core.models import Site
from wagtail.documents.models import get_document_model
from wagtail.images.tests.utils import Image, get_test_image_file

from ..models import Courriel, Scrutin, ScrutinIndex


@pytest.fixture
def document(django_db_setup, django_db_blocker):
    return get_document_model().objects.create(
        title="Test document", file=get_test_image_file()
    )


@pytest.fixture
def image(django_db_setup, django_db_blocker):
    return Image.objects.create(title="Test image", file=get_test_image_file())


@pytest.fixture
def admin(django_db_setup, django_db_blocker):
    return User.objects.get_or_create(
        username="admin",
        defaults={
            'first_name': 'Super',
            'last_name': 'Admin',
            'email': 'admin@amin.admin',
            'is_staff': True,
        },
    )[0]


@pytest.fixture
def liste_scrutin(admin):
    instance = ScrutinIndex(
        live=False, owner=admin, title="Liste des scrutins"
    )
    site = Site.objects.get(is_default_site=True)
    site.root_page.add_child(instance=instance)
    instance.save_revision(user=admin)
    instance.revisions.last().publish()
    return instance


@pytest.fixture
def scrutin(admin, liste_scrutin):
    instance = Scrutin(
        live=False,
        owner=admin,
        title="Assemblée générale !",
        confirmation="Merci de votre participation.",
        peremption=datetime.date.today() + datetime.timedelta(days=30),
        ouvert=True,
    )
    liste_scrutin.add_child(instance=instance)
    instance.form_fields.create(
        label="Approbation du rapport",
        required=True,
        choices='Oui,Non',
        default_value='Oui',
        help_text='Vous devez choisir « <em>Oui</em> » ou « <em>Non</em> ».',
        field_type='radio',
    )
    instance.save_revision(user=admin)
    instance.revisions.last().publish()
    return instance


@pytest.fixture
def pouvoir(scrutin):
    return scrutin.pouvoir_set.create(
        prenom="Jean", nom="Bon", courriels=[Courriel(courriel="jean@bon.fr")]
    )
