from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.template import Context, Template
from datetime import timedelta
from celery import shared_task
import requests
import logging
from .models import Mailing, Client, Message
import pytz
import environ

env = environ.Env()
environ.Env.read_env()


@shared_task(bind=True)
def send_message(self, msg_id):
    try:
        msg = Message.objects.get(pk=msg_id)
    except Exception as e:
        logging.warning(f"Can't retrieve message {msg_id}")
        return

    if msg.mailing.date_end < timezone.now():
        msg.msg_status = Message.CANCELLED
        msg.save()
        logging.warning(f"Message {msg_id} was cancelled due to time limits")
        return
    if msg.mailing.time_start or msg.mailing.time_end:
        timezone.activate(pytz.timezone(msg.client.timezone))
        local_time = timezone.localtime(timezone.now()).time()
        if msg.mailing.time_start < local_time < msg.mailing.time_end:
            msg.msg_status = Message.CANCELLED
            msg.save()
            logging.warning(f"Message {msg_id} was cancelled due to time limits")
            return
    endpoint = env('ENDPOINT_MESSAGE') + str(msg_id)
    token = env('TOKEN')
    headers = {"Authorization": f'Bearer {token}',
               'Content-Type': 'application/json',
               'accept': 'application/json',
               }
    msg_data = {
        'id': msg.pk,
        'phone': msg.client.phone_number,
        'text': msg.mailing.msg_text,
    }
    try:
        req = requests.post(endpoint, headers=headers, json=msg_data)
    except Exception as e:
        logging.error(f"Message {msg_id} was not sent. Error code: {req.status_code}")
        raise self.retry(exc=e, retry_backoff=120, max_retries=None)
    else:
        msg.time_sent = timezone.now()
        msg.msg_status = Message.SENT
        msg.save()
        logging.info(f"Message {msg_id} was sent")


@shared_task(bind=True)
def create_mailing(self, mailing_id):
    try:
        mailing = Mailing.objects.get(pk=mailing_id)
    except Exception as e:
        logging.warning(f"Can't retrieve mailing {mailing_id}")
        return
    if mailing.dispatched and mailing.date_start < timezone.now() < mailing.date_end:
        return
    mailing.dispatched = True
    mailing.save()
    try:
        clients = Client.objects.all()
    except Exception as e:
        logging.warning(f"Can't retrieve clients list")
        return
    if mailing.operator_code_filter:
        clients = clients.filter(operator_code__iexact=mailing.operator_code_filter)
    if mailing.tag_filter:
        clients = clients.filter(tag__iexact=mailing.tag_filter)
    for client in clients:
        new_mailing = Message(mailing=mailing, client=client)
        new_mailing.save()
        send_message.delay(msg_id=new_mailing.pk)


@shared_task()
def collect_mailing():
    for mailing in Mailing.objects.filter(dispatched=False, date_start__lt=timezone.now(), date_end__gt=timezone.now()):
        create_mailing.delay(mailing_id=mailing.pk)


@shared_task(bind=True)
def send_statistics(self):
    subject = 'Notifications statistics'
    template_pattern = '''
    <table>
    {% for mailing in mailings %}
       <tr>
           <td>{{mailing.id}}</td>
            <td>{{mailing.date_start}}</td>
            <td>{{mailing.date_end}}</td>
            <td>{{mailing.all_messages}}</td>
            <td>{{mailing.sent_messages}}</td>
        </tr>
    {% endfor %}
    </table>    
    '''
    template = Template(template_pattern)
    mailings = Mailing.objects.filter(date_start__gte = timezone.now().date()-timedelta(days=1), date_start__lt=timezone.now().date()+timedelta(days=1)).order_by('date_start')
    html_content = template.render(context=Context({'mailings': mailings}))
    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=env('SENDER_EMAIL'),
        to=[env('RECIPIENT_EMAIL')],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()





