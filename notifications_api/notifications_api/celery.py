import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notifications_api.settings')

app = Celery('notifications_api')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every-minute': {
        'task': 'notifications.tasks.collect_mailing',
        'schedule': crontab(),
    },
    'daily-email': {
        'task': 'notifications.tasks.send_stats_email',
        'schedule': crontab(minute=0, hour=10),
    },
}
