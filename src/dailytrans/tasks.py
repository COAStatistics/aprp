from __future__ import absolute_import, unicode_literals
import logging
from celery.task import task
from .models import DailyTran


@task(name="DeleteNotUpdatedTrans")
def delete_not_updated_trans():
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-dailytrans',
    }
    try:
        dailytrans = DailyTran.objects.filter(not_updated__gte=15)
        count = dailytrans.count()
        dailytrans.all().delete()
        db_logger.info('Delete %s not updated dailytrans' % count)

    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
