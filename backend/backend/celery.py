"""
Celery configuration for Kenya Health Access project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('kenya_health_access')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic task schedule
app.conf.beat_schedule = {
    'update-facility-data-daily': {
        'task': 'facilities.tasks.update_facility_data',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'warm-cache-hourly': {
        'task': 'facilities.tasks.warm_cache',
        'schedule': crontab(minute=0),  # Run every hour
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
