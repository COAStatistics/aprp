from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime
from celery.task import task
from .models import Watchlist
from dailytrans.utils import (
    get_query_set,
    get_group_by_date_query_set,
)

db_logger = logging.getLogger('aprp')
logger_extra = {
    'type_code': 'LOT-watchlists',
}


@task(name="DefaultWatchlistMonitorProfileUpdate")
def active_update():
    try:
        month = datetime.now().month

        watchlist = Watchlist.objects.filter(is_default=True).first()
        watchlist_items = watchlist.children()
        monitor_profiles = watchlist.monitorprofile_set.all()

        for profile in monitor_profiles:

            if month not in profile.months.values_list('id', flat=True):
                profile.is_active = False
                profile.save()
                db_logger.info('Profile %s update to False, low season' % profile, extra=logger_extra)
            else:
                items = watchlist_items.filter_by_product(product=profile.product)
                t = profile.type
                query_set = get_query_set(_type=t, items=items)
                q, has_volume, has_weight = get_group_by_date_query_set(query_set)
                tran = q.order_by('date').last()

                if tran:
                    avg_price = tran['avg_price']
                    is_active = profile.active_compare(avg_price)
                    profile.is_active = is_active
                    profile.save()
                    db_logger.info('Profile %s update to %s, latest average price is %s' % (profile, is_active, avg_price), extra=logger_extra)
                else:
                    db_logger.warning('Product %s has no price' % profile.product, extra=logger_extra)

    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
