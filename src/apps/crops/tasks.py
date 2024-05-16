from __future__ import absolute_import, unicode_literals
import logging
from celery.task import task
from .builder import (
    direct_origin,
    direct_wholesale
)


@task(name="DailyWholesaleCropBuilder")
def build_crop_wholesale(delta):
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-crops',
    }
    try:
        result = direct_wholesale(delta=delta)
        if result.success:
            logger_extra['duration'] = result.duration
            db_logger.info(
                f'Successfully process trans:  {result.start_date, result.end_date}',
                extra=logger_extra)
    except Exception as e:
        db_logger.exception(e, extra=logger_extra)


@task(name='DailyOriginCropBuilder')
def build_crop_wholesale(delta):
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-crops',
    }
    try:
        result = direct_origin(delta=delta)
        if result.success:
            logger_extra['duration'] = result.duration
            db_logger.info(
                f'Successfully process trans: {result.start_date, result.end_date}',
                extra=logger_extra)
    except Exception as e:
        db_logger.exception(e, extra=logger_extra)