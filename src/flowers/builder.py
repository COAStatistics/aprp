from dailytrans.builders.amis import Api as WholeSaleApi
from dailytrans.builders.utils import date_delta, product_generator, director, date_generator
from .models import Flower


MODELS = [Flower]
WHOLESALE_DELTA_DAYS = 1
LOGGER_TYPE_CODE = 'LOT-flowers'


@director
def direct(*args):
    direct_wholesale_07(*args)
    direct_wholesale_04(*args)


@director
def direct_wholesale_07(start_date=None, end_date=None, *args):

    config_code = 'COG07'

    for model in MODELS:
        wholesale_api = WholeSaleApi(model=model,
                                     config_code=config_code,
                                     type_id=1,
                                     logger_type_code=LOGGER_TYPE_CODE,
                                     market_type='L')

        for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
            response = wholesale_api.request(date=delta_end_date)
            wholesale_api.load(response)


@director
def direct_wholesale_04(start_date=None, end_date=None, *args):
    config_code = 'COG04'

    for model in MODELS:
        # Provide sum_to_product to calculate detail objects to one DailyTran
        wholesale_api = WholeSaleApi(model=model,
                                     config_code=config_code,
                                     type_id=1,
                                     logger_type_code=LOGGER_TYPE_CODE,
                                     market_type='L',
                                     sum_to_product='L')
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, WHOLESALE_DELTA_DAYS):
            response = wholesale_api.request(date=delta_end_date)
            wholesale_api.load(response)




