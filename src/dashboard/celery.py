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
    # ======================================== 3 day Builder ========================================
    'daily-chicken-builder-3d': {
        'task': 'DailyChickenBuilder',
        'schedule': crontab(minute=5, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    'daily-ram-builder-3d': {
        'task': 'DailyRamBuilder',
        'schedule': crontab(minute=15, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    'daily-goose-builder-3d': {
        'task': 'DailyGooseBuilder',
        'schedule': crontab(minute=25, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    'daily-duck-builder-3d': {
        'task': 'DailyDuckBuilder',
        'schedule': crontab(minute=35, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    'daily-hog-builder-3d': {
        'task': 'DailyHogBuilder',
        'schedule': crontab(minute=45, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    'daily-rice-builder-3d': {
        'task': 'DailyRiceBuilder',
        'schedule': crontab(minute=55, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    'daily-flower-builder-3d': {
        'task': 'DailyFlowerBuilder',
        'schedule': crontab(minute=0, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    'daily-crop-builder-3d': {
        'task': 'DailyCropBuilder',
        'schedule': crontab(minute=10, hour='0,3,6,9,12,15,18,21'),
        'args': (-2,)  # direct 3 day
    },
    'daily-fruit-builder-3d': {
        'task': 'DailyFruitBuilder',
        'schedule': crontab(minute=20, hour='1,4,7,10,13,16,19,22'),
        'args': (-2,)  # direct 3 day
    },
    'daily-seafood-builder-3d': {
        'task': 'DailySeafoodBuilder',
        'schedule': crontab(minute=40, hour='11,14'),
        'args': (-2,)  # direct 3 day
    },
    'daily-cattle-builder-3d': {
        'task': 'DailyCattleBuilder',
        'schedule': crontab(minute=10, hour='*'),
        'args': (-2,)  # direct 3 day
    },
    # ======================================== 2 week Builder ========================================
    'daily-chicken-builder-14d': {
        'task': 'DailyChickenBuilder',
        'schedule': crontab(minute=0, hour='0,11'),
        'args': (-13,)  # direct 14 days range
    },
    'daily-ram-builder-14d': {
        'task': 'DailyRamBuilder',
        'schedule': crontab(minute=0, hour='1,12'),
        'args': (-13,)  # direct 14 days range
    },
    'daily-goose-builder-14d': {
        'task': 'DailyGooseBuilder',
        'schedule': crontab(minute=0, hour='2,13'),
        'args': (-13,)  # direct 14 days range
    },
    'daily-duck-builder-14d': {
        'task': 'DailyDuckBuilder',
        'schedule': crontab(minute=0, hour='3,14'),
        'args': (-13,)  # direct 14 days range
    },
    'daily-hog-builder-14d': {
        'task': 'DailyHogBuilder',
        'schedule': crontab(minute=0, hour='4,15'),
        'args': (-13,)  # direct 14 days range
    },
    'daily-rice-builder-14d': {
        'task': 'DailyRiceBuilder',
        'schedule': crontab(minute=0, hour='5,16'),
        'args': (-13,)  # direct 14 days range
    },
    'daily-flower-builder-14d': {
        'task': 'DailyFlowerBuilder',
        'schedule': crontab(minute=0, hour='6,17'),
        'args': (-13,)  # direct 14 days range
    },
    'daily-crop-builder-14d': {
        'task': 'DailyCropBuilder',
        'schedule': crontab(minute=0, hour='7,18'),  # 2 hour
        'args': (-13,)  # direct 14 days range
    },
    'daily-fruit-builder-14d': {
        'task': 'DailyFruitBuilder',
        'schedule': crontab(minute=0, hour='9,20'),  # 2 hour
        'args': (-13,)  # direct 14 days range
    },
    'daily-seafood-builder-14d': {
        'task': 'DailySeafoodBuilder',
        'schedule': crontab(minute=0, hour='18,22'),  # 2 hour
        'args': (-13,)  # direct 14 days range
    },
    'daily-cattle-builder-14d': {
        'task': 'DailyCattleBuilder',
        'schedule': crontab(minute=30, hour='0, 11'),
        'args': (-13,)  # direct 14 days range
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