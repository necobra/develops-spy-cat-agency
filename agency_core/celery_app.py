import os
from celery import Celery
from celery.signals import worker_ready

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_core.settings')

app = Celery('agency_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

try:
    import agency_core.celery_beat
except ImportError:
    pass

def run_update_breads_once(sender, **kwargs):
    from spycats.tasks import update_breads_from_api
    update_breads_from_api.delay()

worker_ready.connect(run_update_breads_once)
