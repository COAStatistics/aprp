from dailytrans.builders import eir50
from dailytrans.builders.utils import (
    director,
    date_generator,
    DirectData,
)
from .models import Goose


MODELS = [Goose]
CONFIG_CODE = 'COG12'
APIS = [eir50.Api]
DELTA_DAYS = 90
LOGGER_TYPE_CODE = 'LOT-gooses'


@director
def direct(start_date=None, end_date=None, *args, **kwargs):

    data = DirectData(CONFIG_CODE, 2, LOGGER_TYPE_CODE)

    for model in MODELS:
        for Api in APIS:
            api = Api(model=model, **data._asdict())
            for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
                response = api.request(start_date=delta_start_date, end_date=delta_end_date)
                api.load(response)

    return data
