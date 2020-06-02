from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'gvot.base'
    verbose_name = "Base"

    def ready(self):
        from . import signals  # noqa
