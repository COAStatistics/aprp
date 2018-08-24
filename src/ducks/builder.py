from dailytrans.builders import eir51
from dailytrans.builders.utils import date_delta, director, date_generator
from .models import Duck


MODELS = [Duck]
CONFIG_CODE = 'COG11'
APIS = [eir51.Api]
DELTA_DAYS = 90
LOGGER_TYPE_CODE = 'LOT-ducks'


@director
def direct(start_date=None, end_date=None, *args):

    for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
        for model in MODELS:
            for Api in APIS:
                api = Api(model=model, config_code=CONFIG_CODE, type_id=2, logger_type_code=LOGGER_TYPE_CODE)
                response = api.request(start_date=delta_start_date, end_date=delta_end_date)
                api.load(response)




