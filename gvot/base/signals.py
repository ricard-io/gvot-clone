from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.Scrutin)
def association_post_creation_callback(sender, **kwargs):
    if kwargs['created']:
        kwargs['instance'].after_creation()
