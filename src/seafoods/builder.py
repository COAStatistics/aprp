from dailytrans.builders.eir032 import Api as WholeSaleApi
from dailytrans.builders.efish import Api as OriginApi
from dailytrans.builders.utils import date_delta, product_generator, director, date_generator
from .models import Seafood
import time


MODELS = [Seafood]
CONFIG_CODE = 'COG13'
WHOLESALE_DELTA_DAYS = 30
ORIGIN_DELTA_DAYS = 365
LOGGER_TYPE_CODE = 'LOT-seafoods'


@director
def direct(*args):

    direct_wholesale(*args)
    direct_origin(*args)


@director
def direct_wholesale(start_date=None, end_date=None, *args):

    for model in MODELS:
        wholesale_api = WholeSaleApi(model=model, config_code=CONFIG_CODE, type_id=1, logger_type_code=LOGGER_TYPE_CODE)
        for obj in product_generator(model):
            if obj.type.id == 1:
                for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
                    response = wholesale_api.request(start_date=delta_start_date, end_date=delta_end_date, name=obj.name)
                    wholesale_api.load(response)


@director
def direct_origin(start_date=None, end_date=None, *args):

    for model in MODELS:
        origin_api = OriginApi(model=model, config_code=CONFIG_CODE, type_id=2, logger_type_code=LOGGER_TYPE_CODE)
        for obj in product_generator(model):
            if obj.type.id == 2:
                for delta_start_date, delta_end_date in date_generator(start_date, end_date, ORIGIN_DELTA_DAYS):
                    response = origin_api.request(start_date=delta_start_date, end_date=delta_end_date, code=obj.code)
                    origin_api.load(response)
                    # sleep for that poor api service...
                    time.sleep(10)








