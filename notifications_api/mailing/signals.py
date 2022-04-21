from django.db.models import signals
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Mailing
from .tasks import create_mailing


@receiver(post_save, sender=Mailing)
def mailing_post_save(sender, instance, signal, *args, **kwargs):
    if not instance.dispatched and instance.date_start < timezone.now() < instance.date_end:
        create_mailing.delay(mailing_id=instance.pk)
