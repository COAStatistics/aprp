from apps.dailytrans.builders.eir030 import Api as WholeSaleApi05
from apps.dailytrans.builders.apis import Api as OriginApi
from apps.dailytrans.builders.amis import Api as WholeSaleApi02
from apps.dailytrans.builders.utils import (
    product_generator,
    director,
    date_generator,
    DirectData,
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
def direct_wholesale(*args, **kwargs):
    direct_wholesale_05(*args, **kwargs)
    direct_wholesale_02(*args, **kwargs)


@director
def direct_wholesale_05(start_date, end_date, *args, **kwargs):

    data = DirectData('COG05', 1, LOGGER_TYPE_CODE)

    for model in MODELS:
        wholesale_api = WholeSaleApi05(model=model, **data._asdict())

        for obj in product_generator(model, type=1, **kwargs):
            for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
                response = wholesale_api.request(start_date=delta_start_date, end_date=delta_end_date, code=obj.code)
                wholesale_api.load(response)

    return data


@director
def direct_origin(start_date, end_date, *args, **kwargs):

    data = DirectData('COG05', 2, LOGGER_TYPE_CODE)

    for model in MODELS:
        origin_api = OriginApi(model=model, **data._asdict())

        for obj in product_generator(model, type=2, **kwargs):
            for delta_start_date, delta_end_date in date_generator(start_date, end_date, ORIGIN_DELTA_DAYS):
                response = origin_api.request(start_date=delta_start_date, end_date=delta_end_date, name=obj.code)
                origin_api.load(response)

    return data


@director
def direct_wholesale_02(start_date, end_date, *args, **kwargs):

    data = DirectData('COG02', 1, LOGGER_TYPE_CODE)

    for model in MODELS:
        wholesale_api = WholeSaleApi02(model=model, market_type='V', **data._asdict())

        # This api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, 1):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    return data
