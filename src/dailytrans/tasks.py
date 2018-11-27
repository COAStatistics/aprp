from __future__ import absolute_import, unicode_literals
import logging
from celery.task import task
from .models import DailyTran


@task(name="DeleteNotUpdatedTrans")
def delete_not_updated_trans(not_updated_times=15):
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-dailytrans',
    }
    try:
        dailytrans = DailyTran.objects.filter(not_updated__gte=not_updated_times)
        count = dailytrans.count()
        dailytrans.all().delete()
        db_logger.info('Delete %s not updated dailytrans' % count, extra=logger_extra)

    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
