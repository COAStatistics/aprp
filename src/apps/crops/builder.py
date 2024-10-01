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
import datetime

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
        date_diff = end_date - start_date
        for delta in range(date_diff.days + 1):
            response = wholesale_api.request(start_date=start_date + datetime.timedelta(days=delta),
                                             end_date=start_date + datetime.timedelta(days=delta), tc_type='N04')
            wholesale_api.load(response)

    return data


@director
def direct_origin(start_date, end_date, *args, **kwargs):
    data = DirectData('COG05', 2, LOGGER_TYPE_CODE)

    for model in MODELS:
        origin_api = OriginApi(model=model, **data._asdict())
        date_diff = end_date - start_date
        for delta in range(date_diff.days + 1):
            response = origin_api.request(start_date=start_date + datetime.timedelta(days=delta),
                                          end_date=start_date + datetime.timedelta(days=delta), *args, **kwargs)
            origin_api.load(response)
            # response_garlic = origin_api.request(start_date=start_date + datetime.timedelta(days=delta),
            #                                      end_date=start_date + datetime.timedelta(days=delta),
            #                                      name='蒜頭(蒜球)(旬價)')
            # origin_api.load(response_garlic)
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
