import logging
from django.utils import timezone
from dailytrans.builders import (
    eir49,
    eir049,
    eir050,
)
from dailytrans.builders.utils import (
    director,
    date_generator,
)
from dailytrans.models import DailyTran
from .models import Chicken


MODELS = [Chicken]
CONFIG_CODE = 'COG10'
DELTA_DAYS = 7
APIS = [eir49.Api,
        eir049.Api,
        eir050.Api]
LOGGER_TYPE_CODE = 'LOT-chickens'

db_logger = logging.getLogger('aprp')
logger_extra = {
    'type_code': LOGGER_TYPE_CODE,
}


@director
def direct(start_date=None, end_date=None, *args):

    direct_time = timezone.now()

    for model in MODELS:
        for Api in APIS:
            api = Api(model=model, config_code=CONFIG_CODE, type_id=2, logger_type_code=LOGGER_TYPE_CODE)
            for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
                response = api.request(start_date=delta_start_date, end_date=delta_end_date)
                api.load(response)

    qs = DailyTran.objects.filter(product__config__code=CONFIG_CODE,
                                  product__type__id=2,
                                  date__range=[start_date, end_date],
                                  update_time__lte=direct_time)
    if qs:
        db_logger.info('Trans data not updated: %s', str([str(d) for d in qs]), extra=logger_extra)






