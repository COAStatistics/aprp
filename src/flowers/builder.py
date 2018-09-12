import logging
from django.utils import timezone

from dailytrans.builders.amis import Api as WholeSaleApi
from dailytrans.builders.utils import (
    director,
    date_generator,
)
from dailytrans.models import DailyTran
from .models import Flower


MODELS = [Flower]

# This api only provide one day filter
WHOLESALE_DELTA_DAYS = 1
LOGGER_TYPE_CODE = 'LOT-flowers'

db_logger = logging.getLogger('aprp')
logger_extra = {
    'type_code': LOGGER_TYPE_CODE,
}


@director
def direct(*args):
    direct_wholesale_07(*args)
    direct_wholesale_04(*args)


@director
def direct_wholesale_07(start_date=None, end_date=None, *args):

    config_code = 'COG07'
    direct_time = timezone.now()

    for model in MODELS:
        wholesale_api = WholeSaleApi(model=model,
                                     config_code=config_code,
                                     type_id=1,
                                     logger_type_code=LOGGER_TYPE_CODE,
                                     market_type='L')

        # This api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    qs = DailyTran.objects.filter(product__config__code=config_code,
                                  product__type__id=1,
                                  date__range=[start_date, end_date],
                                  update_time__lte=direct_time)
    if qs:
        db_logger.info('Delete old trans item: %s', str([str(d) for d in qs]), extra=logger_extra)
        qs.all().delete()


@director
def direct_wholesale_04(start_date=None, end_date=None, *args):

    config_code = 'COG04'
    direct_time = timezone.now()

    for model in MODELS:
        # Provide sum_to_product to calculate detail objects to one DailyTran
        wholesale_api = WholeSaleApi(model=model,
                                     config_code=config_code,
                                     type_id=1,
                                     logger_type_code=LOGGER_TYPE_CODE,
                                     market_type='L',
                                     sum_to_product='L')

        # This api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    qs = DailyTran.objects.filter(product__config__code=config_code,
                                  product__type__id=1,
                                  date__range=[start_date, end_date],
                                  update_time__lte=direct_time)
    if qs:
        db_logger.info('Delete old trans item: %s', str([str(d) for d in qs]), extra=logger_extra)
        qs.all().delete()




