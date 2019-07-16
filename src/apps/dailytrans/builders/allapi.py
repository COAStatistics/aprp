from apps.cattles.builder import direct as cattles_api
from apps.chickens.builder import direct as chickens_api
from apps.ducks.builder import direct as ducks_api
from apps.flowers.builder import direct as flowers_api
from apps.fruits.builder import direct as fruits_api
from apps.gooses.builder import direct as gooses_api
from apps.hogs.builder import direct as hogs_api
from apps.rams.builder import direct as rams_api
from apps.rices.builder import direct as rices_api
from apps.seafoods.builder import direct as seafoods_api
from apps.dailytrans.builders.utils import director


@director
def direct(start_date=None, end_date=None, *args, **kwargs):
    print('cattles_api')
    cattles_api(start_date, end_date, *args, **kwargs)
    print('chickens_api')
    chickens_api(start_date, end_date, *args, **kwargs)
    print('ducks_api')
    ducks_api(start_date, end_date, *args, **kwargs)
    print('flowers_api')
    flowers_api(start_date, end_date, *args, **kwargs)
    print('fruits_api')
    fruits_api(start_date, end_date, *args, **kwargs)
    print('gooses_api')
    gooses_api(start_date, end_date, *args, **kwargs)
    print('hogs_api')
    hogs_api(start_date, end_date, *args, **kwargs)
    print('rams_api')
    rams_api(start_date, end_date, *args, **kwargs)
    print('rices_api')
    rices_api(start_date, end_date, *args, **kwargs)
    print('seafoods_api')
    seafoods_api(start_date, end_date, *args, **kwargs)
