from __future__ import absolute_import, unicode_literals
import logging
from celery.task import task

db_logger = logging.getLogger('aprp')


@task(name="Beat")
def beat(params):
    print(params)
