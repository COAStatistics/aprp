from dailytrans.builders.eir107 import Api
from dailytrans.builders.utils import (
    director,
    date_generator,
    DirectData,
)
from .models import Ram


MODELS = [Ram]
CONFIG_CODE = 'COG09'
LOGGER_TYPE_CODE = 'LOT-rams'
# Ram api has no date range filter, most set delta_days to 1
DELTA_DAYS = 1


@director
def direct(start_date=None, end_date=None, *args, **kwargs):

    data = DirectData(CONFIG_CODE, 1, LOGGER_TYPE_CODE)

    for model in MODELS:
        api = Api(model=model, **data._asdict())
        for delta_start_date, delta_end_date in date_generator(start_date, end_date, DELTA_DAYS):
            response = api.request(date=delta_start_date)
            api.load(response)

    return data
