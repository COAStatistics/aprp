from dailytrans.builders.rice_avg import Api
from dailytrans.builders.utils import date_delta, director, date_generator
from .models import Rice


MODELS = [Rice]
CONFIG_CODE = 'COG01'
DELTA_DAYS = 30
LOGGER_TYPE_CODE = 'LOT-rices'


@director
def direct(start_date=None, end_date=None, *args):

    for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
        for model in MODELS:
            api = Api(model=model, config_code=CONFIG_CODE, type_id=None, logger_type_code=LOGGER_TYPE_CODE)
            response = api.request(start_date=delta_start_date, end_date=delta_end_date)
            api.load(response)




