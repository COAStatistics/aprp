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


def direct(start_date=None, end_date=None, *args, **kwargs):
    cattles_api(start_date, end_date, *args, **kwargs)
    chickens_api(start_date, end_date, *args, **kwargs)
    ducks_api(start_date, end_date, *args, **kwargs)
    flowers_api(start_date, end_date, *args, **kwargs)
    fruits_api(start_date, end_date, *args, **kwargs)
    gooses_api(start_date, end_date, *args, **kwargs)
    hogs_api(start_date, end_date, *args, **kwargs)
    rams_api(start_date, end_date, *args, **kwargs)
    rices_api(start_date, end_date, *args, **kwargs)
    seafoods_api(start_date, end_date, *args, **kwargs)
