from django.db import models
from django.conf import settings
from django.utils import timezone


import pytz

from .validators import validate_operator_code, validate_phone_number


class Mailing(models.Model):
    msg_text = models.TextField(verbose_name='Message')
    date_start = models.DateTimeField(verbose_name='Start date')
    date_end = models.DateTimeField(verbose_name='End date')
    time_start = models.TimeField(verbose_name='Start time')
    time_end = models.TimeField(verbose_name='End time')
    tag_filter = models.CharField(max_length=128, blank=True, verbose_name='Filter by tag')
    operator_code_filter = models.CharField(max_length=3, validators=[validate_operator_code], blank=True, verbose_name='Filter by operator code')
    dispatched = models.BooleanField(default=False, editable=False, verbose_name='Mailing dispatched')

    def all_messages(self):
        return self.message_set.count()

    def sent_messages(self):
        sent_messages = self.message_set.filter(status=Message.STATUS_SENT).count()
        return sent_messages

    def __str__(self):
        return f'Mailing {self.id} at {self.date_start}'


class Client(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    phone_number = models.CharField(max_length=11, validators=[validate_phone_number], unique=True, verbose_name='Phone number')
    operator_code = models.CharField(max_length=3, validators=[validate_operator_code], verbose_name='Operator code')
    timezone = models.CharField(max_length=100, choices=TIMEZONES, default=settings.TIME_ZONE, verbose_name='Timezone')
    tag = models.CharField(max_length=128, blank=True, verbose_name='Tag')

    def save(self, *args, **kwargs):
        if not self.operator_code:
            self.operator_code = str(self.phone_number)[1:4]
        return super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return f'Client number {self.phone_number}'


class Message(models.Model):
    SENT = 'sent'
    AWAITS = 'awaits'
    CANCELLED = 'cancelled'

    MESSAGE_STATUSES = (
        (SENT, 'sent'),
        (AWAITS, 'awaits'),
        (CANCELLED, 'cancelled'),
    )

    time_sent = models.DateTimeField(null=True, verbose_name='Sent time')
    msg_status = models.CharField(choices=MESSAGE_STATUSES, default=AWAITS, verbose_name='Message status')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Mailing')

# Create your models here.
