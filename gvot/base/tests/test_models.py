from django.contrib.auth.models import User

import pytest
from wagtail.core.models import Page, Site

from ..models import SitePage


@pytest.mark.django_db
class TestSitePage:
    def test_draft_creation(self):
        owner = User.objects.get_or_create(username="Anne")[0]
        instance = SitePage(live=False, owner=owner, title="title")
        assert instance

    def test_add_draft_in_arborescence(self):
        owner = User.objects.get_or_create(username="Anne")[0]
        instance = SitePage(live=False, owner=owner, title="title")
        assert not instance.path

        site = Site.objects.get(is_default_site=True)
        site.root_page.add_child(instance=instance)
        instance.save_revision(user=owner)

        assert instance.path
        assert site.root_page.get_children().count()
        assert not site.root_page.get_children().live().count()

    def test_publish_in_arborescence(self):
        owner = User.objects.get_or_create(username="Anne")[0]
        instance = SitePage(live=False, owner=owner, title="title")
        assert not instance.path

        site = Site.objects.get(is_default_site=True)
        site.root_page.add_child(instance=instance)
        instance.save_revision(user=owner)
        instance.revisions.last().publish()

        assert instance.path
        assert site.root_page.get_children().live().count()

    def test_no_more_wagtail_page_in_arborescence(self):
        site = Site.objects.get(is_default_site=True)
        owner = User.objects.get_or_create(username="Anne")[0]
        instance = Page(live=False, owner=owner, title="title")
        assert not instance.can_create_at(site.root_page)
