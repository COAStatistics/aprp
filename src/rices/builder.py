import logging
from django.utils import timezone

from dailytrans.builders.rice_avg import Api
from dailytrans.builders.utils import (
    director,
    date_generator,
)
from dailytrans.models import DailyTran
from .models import Rice


MODELS = [Rice]
CONFIG_CODE = 'COG01'
DELTA_DAYS = 30
LOGGER_TYPE_CODE = 'LOT-rices'

db_logger = logging.getLogger('aprp')
logger_extra = {
    'type_code': LOGGER_TYPE_CODE,
}


@director
def direct(start_date=None, end_date=None, *args):

    direct_time = timezone.now()

    for model in MODELS:
        api = Api(model=model, config_code=CONFIG_CODE, type_id=None, logger_type_code=LOGGER_TYPE_CODE)
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
            response = api.request(start_date=delta_start_date, end_date=delta_end_date)
            api.load(response)

    qs = DailyTran.objects.filter(product__config__code=CONFIG_CODE,
                                  date__range=[start_date, end_date],
                                  update_time__lte=direct_time)
    if qs:
        db_logger.warning('Trans data not updated: %s', str([str(d) for d in qs]), extra=logger_extra)



