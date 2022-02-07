from apps.dailytrans.builders.naifchickens import Api
from apps.dailytrans.builders.utils import (
    product_generator,
    director,
    DirectData,
)
from .models import Naifchickens
from datetime import timedelta,date
import json

MODELS = [Naifchickens]
CONFIG_CODE = 'COG16'
LOGGER_TYPE_CODE = 'LOT-naifchickens'
TYPE_ID = 1     # 1:批發; 2:產地; 3:零售
DELTA_DAYS = 30

@director
def direct(start_date=None, end_date=None, *args, **kwargs):

    data = DirectData(CONFIG_CODE, TYPE_ID, LOGGER_TYPE_CODE)

    distinct_list = []

    for model in MODELS:
        api = Api(model=model, **data._asdict())
        for obj in product_generator(model, type=TYPE_ID, **kwargs):
            if not start_date:
                start_date = (date.today() - timedelta(days=DELTA_DAYS)).strftime('%Y/%m/%d')
            if not end_date:
                end_date = date.today().strftime('%Y/%m/%d')

            # 白肉雞總貨和紅羽土雞總貨是同一網頁頁面,選其中一個,兩品項會一起抓,避免花時間重複抓
            distinct_list.append(obj.id)
            if (obj.id == 150004 and 150003 in distinct_list) or (obj.id == 150003 and 150004 in distinct_list):    
                continue

            response = api.request(start_date=start_date, end_date=end_date, id=obj.id)
            if response:
                api.load(json.dumps(response))

    return data