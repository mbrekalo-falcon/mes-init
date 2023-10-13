from __future__ import absolute_import
import json
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


""" EXAMPLE
app.conf.CELERYBEAT_SCHEDULE = {
    
    'eternity_message': {
        'task': 'send_em_message',
        'schedule': crontab(minute=30),
    },
    'schedule_interval_system_constants': {
        'task': 'schedule_interval_system_constants',
        'schedule': crontab(minute=5),
    },
}
"""