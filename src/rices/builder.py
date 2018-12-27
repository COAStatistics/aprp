from dailytrans.builders.rice_avg import Api
from dailytrans.builders.utils import (
    director,
    date_generator,
    DirectData,
)
from .models import Rice


MODELS = [Rice]
CONFIG_CODE = 'COG01'
DELTA_DAYS = 30
LOGGER_TYPE_CODE = 'LOT-rices'


@director
def direct(start_date=None, end_date=None, *args):

    data = DirectData(CONFIG_CODE, None, LOGGER_TYPE_CODE)

    for model in MODELS:
        api = Api(model=model, **data._asdict())
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
            response = api.request(start_date=delta_start_date, end_date=delta_end_date)
            api.load(response)

    return data
