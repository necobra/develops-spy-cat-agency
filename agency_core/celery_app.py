import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_core.settings')

app = Celery('agency_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

try:
    import agency_core.celery_beat
except ImportError:
    pass

