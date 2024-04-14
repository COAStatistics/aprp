import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery_worker():
    cmd = "pkill -9 celery"
    subprocess.call(shlex.split(cmd))
    cmd = 'celery worker --app=dashboard --pool=eventlet --concurrency=4  --loglevel=info'
    subprocess.call(shlex.split(cmd))


class Command(BaseCommand):
    def handle(self, *args, **options):
        autoreload.python_reloader(restart_celery_worker)
