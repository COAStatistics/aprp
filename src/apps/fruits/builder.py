import datetime
import time

from apps.dailytrans.builders.eir030 import Api as WholeSaleApi06
from apps.dailytrans.builders.apis import Api as OriginApi
from apps.dailytrans.builders.amis import Api as WholeSaleApi03
from apps.dailytrans.builders.utils import (
    product_generator,
    director,
    date_generator,
    DirectData,
)
from .models import Fruit

MODELS = [Fruit]
LOGGER_TYPE_CODE = 'LOT-fruits'
WHOLESALE_DELTA_DAYS = 30
ORIGIN_DELTA_DAYS = 30


@director
def direct(*args, **kwargs):
    direct_wholesale_06(*args, **kwargs)
    direct_origin(*args, **kwargs)
    direct_wholesale_03(*args, **kwargs)


@director
def direct_wholesale_06(start_date=None, end_date=None, *args, **kwargs):
    data = DirectData('COG06', 1, LOGGER_TYPE_CODE)
    for model in MODELS:
        start = time.time()
        wholesale_api = WholeSaleApi06(model=model, **data._asdict())
        date_diff = end_date - start_date
        for delta in range(date_diff.days + 1):
            response = wholesale_api.request(start_date=start_date + datetime.timedelta(days=delta),
                                             end_date=start_date + datetime.timedelta(days=delta), tc_type='N05')
            wholesale_api.load(response)
    return data


@director
def direct_origin(start_date=None, end_date=None, *args, **kwargs):
    data = DirectData('COG06', 2, LOGGER_TYPE_CODE)

    for model in MODELS:
        origin_api = OriginApi(model=model, **data._asdict())
        date_diff = end_date - start_date
        for delta in range(date_diff.days + 1):
            response = origin_api.request(start_date=start_date + datetime.timedelta(days=delta),
                                          end_date=start_date + datetime.timedelta(days=delta), *args, **kwargs)
            origin_api.load(response)
            # response_banana_low = origin_api.request(start_date=start_date + datetime.timedelta(days=delta),
            #                                          end_date=start_date + datetime.timedelta(days=delta),
            #                                          name='青香蕉下品(內銷)')
            # origin_api.load(response_banana_low)
    return data


@director
def direct_wholesale_03(start_date=None, end_date=None, *args, **kwargs):
    data = DirectData('COG03', 1, LOGGER_TYPE_CODE)

    for model in MODELS:
        wholesale_api = WholeSaleApi03(model=model, market_type='F', **data._asdict())

        # this api only provide one day filter
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, 1):
            response = wholesale_api.request(date=delta_start_date)
            wholesale_api.load(response)

    return data
