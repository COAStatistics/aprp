from __future__ import absolute_import, unicode_literals
import logging
from datetime import datetime
from celery.task import task
from .models import Watchlist
from apps.dailytrans.utils import (
    get_query_set,
    get_group_by_date_query_set,
)


@task(name="DefaultWatchlistMonitorProfileUpdate")
def active_update():
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-watchlists',
    }
    try:
        month = datetime.now().month

        watchlist = Watchlist.objects.filter(is_default=True).first()
        watchlist_items = watchlist.children()
        monitor_profiles = watchlist.monitorprofile_set.all()

        activated = []
        deactivated = []
        start_time = datetime.now()

        for profile in monitor_profiles:

            if month not in profile.months.values_list('id', flat=True):
                # for logging
                if profile.is_active:
                    deactivated.append(profile)

                profile.is_active = False
                profile.save()

            else:
                items = watchlist_items.filter_by_product(product=profile.product)
                t = profile.type
                query_set = get_query_set(_type=t, items=items)
                q, has_volume, has_weight = get_group_by_date_query_set(query_set)
                tran = q.sort_values('date').iloc[-1]

                if tran.empty:
                    db_logger.warning(
                        f'Product {profile.product} has no price',
                        extra=logger_extra,
                    )

                elif watchlist.start_date <= tran['date'] <= watchlist.end_date and tran["date"].month in profile.months.values_list('id', flat=True):
                    avg_price = tran['avg_price']
                    is_active = profile.active_compare(avg_price)
                    # for logging
                    if profile.is_active is not is_active:
                        if profile.is_active:
                            deactivated.append(profile)
                        else:
                            activated.append(profile)

                    profile.is_active = is_active
                    profile.save()

        end_time = datetime.now()
        logger_extra['duration'] = end_time - start_time

        db_logger.info(
            f'Updated default watchlist profiles successfully, activate: {activated}, deactivate: {deactivated}'
            , extra=logger_extra)

    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
