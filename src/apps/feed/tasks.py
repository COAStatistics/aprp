from __future__ import absolute_import, unicode_literals
import logging
from celery.task import task
from .builder import direct


@task(name="DailyFeedBuilder")
def build_feed(delta):
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-feed',
    }
    try:
        result = direct(delta=delta)
        if result.success:
            logger_extra['duration'] = result.duration
            db_logger.info('Successfully process trans: %s - %s' % (result.start_date, result.end_date), extra=logger_extra)
    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
