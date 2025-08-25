from celery.schedules import crontab
from agency_core.celery_app import app

app.conf.beat_schedule = {
    'update-breads-every-6-hours': {
        'task': 'spycats.tasks.update_breads_from_api',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}

