from django.utils import timezone
import logging
from dailytrans.builders.cattle import Api
from dailytrans.builders.utils import (
    director,
    date_generator,
)
from dailytrans.models import DailyTran
from .models import Cattle


MODELS = [Cattle]
CONFIG_CODE = 'COG14'
LOGGER_TYPE_CODE = 'LOT-cattles'
# Cattle api has no date range filter, most set date_delta to 1
DELTA_DAYS = 1

db_logger = logging.getLogger('aprp')
logger_extra = {
    'type_code': LOGGER_TYPE_CODE,
}


@director
def direct(start_date=None, end_date=None, *args):

    direct_time = timezone.now()

    for model in MODELS:
        api = Api(model=model, config_code=CONFIG_CODE, type_id=2, logger_type_code=LOGGER_TYPE_CODE)
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
            response = api.request(date=delta_start_date)
            api.load(response)

    qs = DailyTran.objects.filter(product__config__code=CONFIG_CODE,
                                  product__type__id=2,
                                  date__range=[start_date, end_date],
                                  update_time__lte=direct_time)
    if qs:
        db_logger.info('Delete old trans item: %s', str([str(d) for d in qs]), extra=logger_extra)
        qs.all().delete()
