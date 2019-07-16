from apps.dailytrans.builders import (
    eir49,
    eir049,
    eir050,
)
from apps.dailytrans.builders.utils import (
    director,
    date_generator,
    DirectData,
)
from .models import Chicken


MODELS = [Chicken]
CONFIG_CODE = 'COG10'
DELTA_DAYS = 7
APIS = [eir49.Api,
        eir049.Api,
        eir050.Api]
LOGGER_TYPE_CODE = 'LOT-chickens'


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
