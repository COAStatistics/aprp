from dailytrans.builders.eir030 import Api as WholeSaleApi06
from dailytrans.builders.apis import Api as OriginApi
from dailytrans.builders.amis import Api as WholeSaleApi03
from dailytrans.builders.utils import (
    product_generator,
    director,
    date_generator,
)
from .models import Fruit


MODELS = [Fruit]
LOGGER_TYPE_CODE = 'LOT-fruits'
WHOLESALE_DELTA_DAYS = 30
ORIGIN_DELTA_DAYS = 30


@director
def direct(*args):
    direct_wholesale_06(*args)
    direct_origin(*args)
    direct_wholesale_03(*args)


@director
def direct_wholesale_06(start_date=None, end_date=None, *args):

    kwargs = {
        'config_code': 'COG06',
        'type_id': 1,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        wholesale_api = WholeSaleApi06(model=model, **kwargs)

        for obj in product_generator(model):
            if obj.type.id == 1:
                for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
                    response = wholesale_api.request(start_date=delta_start_date, end_date=delta_end_date, code=obj.code)
                    wholesale_api.load(response)

    return kwargs


@director
def direct_origin(start_date=None, end_date=None, *args):

    kwargs = {
        'config_code': 'COG06',
        'type_id': 2,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        origin_api = OriginApi(model=model, **kwargs)
        for obj in product_generator(model):
            if obj.type.id == 2:
                for delta_start_date, delta_end_date in date_generator(start_date, end_date, ORIGIN_DELTA_DAYS):
                    response = origin_api.request(start_date=delta_start_date, end_date=delta_end_date, name=obj.code)
                    origin_api.load(response)

    return kwargs


@director
def direct_wholesale_03(start_date=None, end_date=None, *args):

    kwargs = {
        'config_code': 'COG03',
        'type_id': 1,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        wholesale_api = WholeSaleApi03(model=model, market_type='F', **kwargs)

        # this api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, 1):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    return kwargs

