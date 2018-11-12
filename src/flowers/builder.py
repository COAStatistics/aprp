from dailytrans.builders.amis import Api as WholeSaleApi
from dailytrans.builders.utils import (
    director,
    date_generator,
)
from .models import Flower


MODELS = [Flower]

# This api only provide one day filter
WHOLESALE_DELTA_DAYS = 1
LOGGER_TYPE_CODE = 'LOT-flowers'


@director
def direct(*args):
    direct_wholesale_07(*args)
    direct_wholesale_04(*args)


@director
def direct_wholesale_07(start_date=None, end_date=None, *args):

    kwargs = {
        'config_code': 'COG07',
        'type_id': 1,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        wholesale_api = WholeSaleApi(model=model, market_type='L', **kwargs)

        # This api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    return kwargs


@director
def direct_wholesale_04(start_date=None, end_date=None, *args):

    kwargs = {
        'config_code': 'COG04',
        'type_id': 1,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        # Provide sum_to_product to calculate detail objects to one DailyTran
        wholesale_api = WholeSaleApi(model=model, market_type='L', sum_to_product='L', **kwargs)

        # This api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    return kwargs





