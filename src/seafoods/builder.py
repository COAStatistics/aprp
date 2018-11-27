import time
from dailytrans.builders.eir032 import Api as WholeSaleApi
from dailytrans.builders.efish import Api as OriginApi
from dailytrans.builders.utils import (
    product_generator,
    director,
    date_generator,
    DirectData,
)
from .models import Seafood


MODELS = [Seafood]
CONFIG_CODE = 'COG13'
WHOLESALE_DELTA_DAYS = 30
ORIGIN_DELTA_DAYS = 90
LOGGER_TYPE_CODE = 'LOT-seafoods'


@director
def direct(*args, **kwargs):

    direct_wholesale(*args, **kwargs)
    direct_origin(*args, **kwargs)


@director
def direct_wholesale(start_date=None, end_date=None, *args, **kwargs):

    data = DirectData(CONFIG_CODE, 1, LOGGER_TYPE_CODE)

    for model in MODELS:
        wholesale_api = WholeSaleApi(model=model, **data._asdict())
        for obj in product_generator(model):
            if obj.type.id == 1:
                for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
                    response = wholesale_api.request(start_date=delta_start_date, end_date=delta_end_date, name=obj.name)
                    wholesale_api.load(response)

    return data


@director
def direct_origin(start_date=None, end_date=None, *args, **kwargs):

    data = DirectData(CONFIG_CODE, 2, LOGGER_TYPE_CODE)

    for model in MODELS:
        origin_api = OriginApi(model=model, **data._asdict())
        for obj in product_generator(model):
            if obj.type.id == 2:
                for delta_start_date, delta_end_date in date_generator(start_date, end_date, ORIGIN_DELTA_DAYS):
                    response = origin_api.request(start_date=delta_start_date, end_date=delta_end_date, code=obj.code)
                    origin_api.load(response)
                    # sleep for that poor api service...
                    time.sleep(10)

    return data








