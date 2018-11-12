from dailytrans.builders import eir50
from dailytrans.builders.utils import (
    director,
    date_generator,
)
from .models import Goose


MODELS = [Goose]
CONFIG_CODE = 'COG12'
APIS = [eir50.Api]
DELTA_DAYS = 90
LOGGER_TYPE_CODE = 'LOT-gooses'


@director
def direct(start_date=None, end_date=None, *args):

    kwargs = {
        'config_code': CONFIG_CODE,
        'type_id': 2,
        'logger_type_code': LOGGER_TYPE_CODE,
    }

    for model in MODELS:
        for Api in APIS:
            api = Api(model=model, **kwargs)
            for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
                response = api.request(start_date=delta_start_date, end_date=delta_end_date)
                api.load(response)

    return kwargs





