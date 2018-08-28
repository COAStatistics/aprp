from __future__ import absolute_import, unicode_literals
import logging
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
        watchlist = Watchlist.objects.filter(is_default=True).first()
        watchlist_items = watchlist.children()
        monitor_profiles = watchlist.monitorprofile_set.all()

        for profile in monitor_profiles:

            items = watchlist_items.filter_by_product(product=profile.product)
            t = profile.type
            query_set = get_query_set(_type=t, items=items)
            q, has_volume, has_weight = get_group_by_date_query_set(query_set)
            tran = q.order_by('date').last()

            if tran:
                avg_price = tran['avg_price']
                is_active = profile.is_active(avg_price)
                profile.active = is_active
                profile.save()
                print('profile %s update to %s, latest price is %s' % (profile, is_active, avg_price))
            else:
                print('product %s no price' % profile.product)

    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
