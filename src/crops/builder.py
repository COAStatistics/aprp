from dailytrans.builders.eir030 import Api as WholeSaleApi05
from dailytrans.builders.apis import Api as OriginApi
from dailytrans.builders.amis import Api as WholeSaleApi02
from dailytrans.builders.utils import (
    product_generator,
    director,
    date_generator,
)
from .models import Crop

MODELS = [Crop]
WHOLESALE_DELTA_DAYS = 30
ORIGIN_DELTA_DAYS = 30
LOGGER_TYPE_CODE = 'LOT-crops'


@director
def direct(*args, **kwargs):

    direct_wholesale_05(*args, **kwargs)
    direct_origin(*args, **kwargs)
    direct_wholesale_02(*args, **kwargs)


@director
def direct_wholesale_05(start_date, end_date, *args):

    kwargs = {
        'config_code': 'COG05',
        'type_id': 1,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        wholesale_api = WholeSaleApi05(model=model, **kwargs)

        for obj in product_generator(model):
            if obj.type.id == 1:
                for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
                    response = wholesale_api.request(start_date=delta_start_date, end_date=delta_end_date, code=obj.code)
                    wholesale_api.load(response)

    return kwargs


@director
def direct_origin(start_date, end_date, *args):

    kwargs = {
        'config_code': 'COG05',
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
def direct_wholesale_02(start_date, end_date, *args):

    kwargs = {
        'config_code': 'COG02',
        'type_id': 1,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        wholesale_api = WholeSaleApi02(model=model, market_type='V', **kwargs)

        # This api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, 1):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    return kwargs






