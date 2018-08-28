from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import datetime


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

app = Celery('dashboard')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app 
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # ======================================== Job ========================================
    'monitor_profile_active_update': {
        'task': 'DefaultWatchlistMonitorProfileUpdate',
        'schedule': crontab(minute='*/15'),
    },
    # ======================================== Daily Builder ========================================
    'daily-chicken-builder-1d': {
        'task': 'DailyChickenBuilder',
        'schedule': crontab(minute=5, hour='*'),
        'args': (0,)  # direct today
    },
    'daily-ram-builder-1d': {
        'task': 'DailyRamBuilder',
        'schedule': crontab(minute=15, hour='*'),
        'args': (0,)  # direct today
    },
    'daily-goose-builder-1d': {
        'task': 'DailyGooseBuilder',
        'schedule': crontab(minute=25, hour='*'),
        'args': (0,)  # direct today
    },
    'daily-duck-builder-1d': {
        'task': 'DailyDuckBuilder',
        'schedule': crontab(minute=35, hour='*'),
        'args': (0,)  # direct today
    },
    'daily-hog-builder-1d': {
        'task': 'DailyHogBuilder',
        'schedule': crontab(minute=45, hour='*'),
        'args': (0,)  # direct today
    },
    'daily-rice-builder-1d': {
        'task': 'DailyRiceBuilder',
        'schedule': crontab(minute=55, hour='*'),
        'args': (0,)  # direct today
    },
    'daily-flower-builder-1d': {
        'task': 'DailyFlowerBuilder',
        'schedule': crontab(minute=0, hour='*'),
        'args': (0,)  # direct today
    },
    'daily-crop-builder-1d': {
        'task': 'DailyCropBuilder',
        'schedule': crontab(minute=10, hour='0,3,6,9,12,15,18,21'),
        'args': (0,)  # direct today
    },
    'daily-fruit-builder-1d': {
        'task': 'DailyFruitBuilder',
        'schedule': crontab(minute=20, hour='1,4,7,10,13,16,19,22'),
        'args': (0,)  # direct today
    },
    'daily-seafood-builder-1d': {
        'task': 'DailySeafoodBuilder',
        'schedule': crontab(minute=40, hour='11,14'),
        'args': (0,)  # direct today
    },
    'daily-cattle-builder-1d': {
        'task': 'DailyCattleBuilder',
        'schedule': crontab(minute=10, hour='*'),
        'args': (0,)  # direct today
    },
    # ======================================== Weekly Builder ========================================
    'daily-chicken-builder-7d': {
        'task': 'DailyChickenBuilder',
        'schedule': crontab(minute=0, hour='0,11'),
        'args': (-7,)  # direct 7 days range
    },
    'daily-ram-builder-7d': {
        'task': 'DailyRamBuilder',
        'schedule': crontab(minute=0, hour='1,12'),
        'args': (-7,)  # direct 7 days range
    },
    'daily-goose-builder-7d': {
        'task': 'DailyGooseBuilder',
        'schedule': crontab(minute=0, hour='2,13'),
        'args': (-7,)  # direct 7 days range
    },
    'daily-duck-builder-7d': {
        'task': 'DailyDuckBuilder',
        'schedule': crontab(minute=0, hour='3,14'),
        'args': (-7,)  # direct 7 days range
    },
    'daily-hog-builder-7d': {
        'task': 'DailyHogBuilder',
        'schedule': crontab(minute=0, hour='4,15'),
        'args': (-7,)  # direct 7 days range
    },
    'daily-rice-builder-7d': {
        'task': 'DailyRiceBuilder',
        'schedule': crontab(minute=0, hour='5,16'),
        'args': (-7,)  # direct 7 days range
    },
    'daily-flower-builder-7d': {
        'task': 'DailyFlowerBuilder',
        'schedule': crontab(minute=0, hour='6,17'),
        'args': (-7,)  # direct 7 days range
    },
    'daily-crop-builder-7d': {
        'task': 'DailyCropBuilder',
        'schedule': crontab(minute=0, hour='7,18'),  # 2 hour
        'args': (-7,)  # direct 7 days range
    },
    'daily-fruit-builder-7d': {
        'task': 'DailyFruitBuilder',
        'schedule': crontab(minute=0, hour='9,20'),  # 2 hour
        'args': (-7,)  # direct 7 days range
    },
    'daily-seafood-builder-7d': {
        'task': 'DailySeafoodBuilder',
        'schedule': crontab(minute=0, hour='18,22'),  # 2 hour
        'args': (-7,)  # direct 7 days range
    },
    'daily-cattle-builder-7d': {
        'task': 'DailyCattleBuilder',
        'schedule': crontab(minute=30, hour='0, 11'),
        'args': (-7,)  # direct 7 days range
    },
    'beat-per-minute': {
        'task': 'Beat',
        'schedule': 60.0,
        'args': (datetime.datetime.now(),),
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))