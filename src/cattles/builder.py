from dailytrans.builders.cattle import Api
from dailytrans.builders.utils import date_delta, director, date_generator
from .models import Cattle


MODELS = [Cattle]
CONFIG_CODE = 'COG14'
LOGGER_TYPE_CODE = 'LOT-cattles'


@director
def direct(start_date=None, end_date=None, *args):
    # Cattle api has no date range filter, most set date_delta to 1
    for delta_start_date, delta_end_date in date_generator(start_date, end_date, 1):
        for model in MODELS:
            api = Api(model=model, config_code=CONFIG_CODE, type_id=2, logger_type_code=LOGGER_TYPE_CODE)
            response = api.request(date=delta_start_date)
            api.load(response)
