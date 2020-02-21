import pytest
from wagtail.documents.models import get_document_model
from wagtail.images.tests.utils import Image, get_test_image_file


@pytest.fixture
def document(django_db_setup, django_db_blocker):
    return get_document_model().objects.create(
        title="Test document", file=get_test_image_file()
    )


@pytest.fixture
def image(django_db_setup, django_db_blocker):
    return Image.objects.create(title="Test image", file=get_test_image_file())
