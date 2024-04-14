import os
import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


PIDFILE = os.environ.get("PIDFILE", "/opt/celeryd.pid")


def restart_celery_beat():
    cmd = "pkill -9 celery"
    subprocess.call(shlex.split(cmd))
    cmd = f"celery beat --app=dashboard --loglevel=info --pidfile={PIDFILE}"
    subprocess.call(shlex.split(cmd))


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting celery beat with autoreload...")
        try:
            os.remove("celeryd.pid")
        except FileNotFoundError as e:
            print(e)

        autoreload.main(restart_celery_beat)
