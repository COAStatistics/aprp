from __future__ import absolute_import, unicode_literals
import logging
from celery.task import task
from .builder import (
    direct_origin,
    direct_wholesale,
)


@task(name="DailyWholesaleSeafoodBuilder")
def build_seafood_wholesale(delta):
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-seafoods',
    }
    try:
        result = direct_wholesale(delta=delta)
        if result.success:
            logger_extra['duration'] = result.duration
            db_logger.info('Successfully process wholesale trans: %s - %s' % (result.start_date, result.end_date), extra=logger_extra)
    except Exception as e:
        db_logger.exception(e, extra=logger_extra)


@task(name="DailyOriginSeafoodBuilder")
def build_seafood_origin(delta):
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-seafoods',
    }
    try:
        result = direct_origin(delta=delta)
        if result.success:
            logger_extra['duration'] = result.duration
            db_logger.info('Successfully process origin trans: %s - %s' % (result.start_date, result.end_date), extra=logger_extra)
    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
