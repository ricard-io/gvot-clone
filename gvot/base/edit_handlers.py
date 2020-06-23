from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from wagtail.admin.edit_handlers import EditHandler

User = get_user_model()


class ResultsPanel(EditHandler):
    template = "modeladmin/results.html"

    def render(self):
        from .models import Pouvoir

        participation = (
            Pouvoir.objects.filter(vote__page=self.instance).distinct().count()
        )
        expression = self.instance.vote_set.all().count()
        results = self.instance.results_distribution()
        return mark_safe(
            render_to_string(
                self.template,
                {
                    'expression': expression,
                    'participation': participation,
                    'results': results,
                },
            )
        )


class AttendeesPanel(EditHandler):
    template = "modeladmin/attendees.html"

    def render(self):
        from .models import Pouvoir

        emargement = Pouvoir.objects.filter(
            vote__page=self.instance
        ).distinct()
        participation = emargement.count()
        expression = self.instance.vote_set.all().count()
        return mark_safe(
            render_to_string(
                self.template,
                {
                    'expression': expression,
                    'participation': participation,
                    'emargement': emargement.values(),
                },
            )
        )
