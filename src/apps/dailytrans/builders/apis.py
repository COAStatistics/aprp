from django.db.models import Q
import datetime
import json
import re
from .utils import date_transfer
from .abstract import AbstractApi
from apps.dailytrans.models import DailyTran
import urllib3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()


def _access_garlic_data_from_api(data):
    data['PERIOD'] = (f"{data['YEAR']}/{data['MONTH']}/"
                      f"{(5 if data['PERIOD'] == '上旬' else 15 if data['PERIOD'] == '中旬' else 25)}")

    data.pop('fun')
    data.pop('YEAR')
    data.pop('MONTH')

    data['PRODUCTNAME'] = '蒜頭(蒜球)(旬價)'

    return data


class Api(AbstractApi):
    # Settings
    API_NAME = 'apis'
    ZFILL = False
    ROC_FORMAT = False
    SEP = '/'

    # Filters
    START_DATE_FILTER = 'startYear=%s&startMonth=%s&startDay=%s'
    END_DATE_FILTER = 'endYear=%s&endMonth=%s&endDay=%s'
    NAME_FILTER = 'productName=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):
        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_name = dic.get('PRODUCTNAME')
        source_name = dic.get('ORGNAME')
        product = self.PRODUCT_QS.filter(code=product_name).first()
        source = self.SOURCE_QS.filter(name=source_name).first()
        if product and source:
            tran = DailyTran(
                product=product,
                source=source,
                avg_price=float(dic.get('AVGPRICE')),
                date=date_transfer(sep=self.SEP, string=dic.get('PERIOD'), roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if product_name and not product:
                self.LOGGER.warning('Cannot Match Product: %s' % (product_name),
                                    extra=self.LOGGER_EXTRA)
            if source_name and source_name != '當日平均價' and not source:
                self.LOGGER.warning('Cannot Match Source: %s' % (source_name),
                                    extra=self.LOGGER_EXTRA)
            return dic

    def hook2(self, dic):
        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_name = "青香蕉下品(內銷)"
        source_name = dic.get('ORGNAME')
        product = self.PRODUCT_QS.filter(code=product_name).first()
        source = self.SOURCE_QS.filter(name=source_name).first()
        if product and source:
            tran = DailyTran(
                product=product,
                source=source,
                avg_price=float(dic.get('AVGPRICE')),
                date=date_transfer(sep=self.SEP, string=dic.get('PERIOD'), roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if product_name and not product:
                self.LOGGER.warning('Cannot Match Product: %s' % (product_name),
                                    extra=self.LOGGER_EXTRA)
            if source_name and source_name != '當日平均價' and not source:
                self.LOGGER.warning('Cannot Match Source: %s' % (source_name),
                                    extra=self.LOGGER_EXTRA)
            return dic

    def hook3(self, dic):
        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_name = "蒜頭(蒜球)(旬價)"
        source_name = dic.get('ORGNAME')
        YEAR = dic.get('YEAR')
        MONTH = dic.get('MONTH')
        PERIOD = dic.get('PERIOD')
        if PERIOD == None:
            pass
        elif '上旬' in PERIOD:
            PERIOD = '05'
        elif '中旬' in PERIOD:
            PERIOD = '15'
        elif '下旬' in PERIOD:
            PERIOD = '25'

        if PERIOD == None:
            pass
        else:
            date = f'{YEAR}/{MONTH}/{PERIOD}'

        product = self.PRODUCT_QS.filter(code=product_name).first()
        source = self.SOURCE_QS.filter(name=source_name).first()
        if product and source:
            tran = DailyTran(
                product=product,
                source=source,
                avg_price=float(dic.get('AVGPRICE')),
                date=date_transfer(sep=self.SEP, string=date, roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if product_name and not product:
                self.LOGGER.warning('Cannot Match Product: %s' % (product_name),
                                    extra=self.LOGGER_EXTRA)
            if source_name and not source:
                self.LOGGER.warning('Cannot Match Source: %s' % (source_name),
                                    extra=self.LOGGER_EXTRA)
            return dic

    def request(self, start_date=None, end_date=None, *args, **kwargs):
        url = self.API_URL
        name = kwargs.get('name') if kwargs.get('name') else None
        if start_date:
            if not isinstance(start_date, datetime.date):
                raise NotImplementedError

            url = '&'.join((url, self.START_DATE_FILTER % (start_date.year, start_date.month, start_date.day)))

        if end_date:
            if not isinstance(end_date, datetime.date):
                raise NotImplementedError

            url = '&'.join((url, self.END_DATE_FILTER % (end_date.year, end_date.month, end_date.day)))
        if start_date and end_date:
            if start_date > end_date:
                raise AttributeError

        url = '&'.join((url, self.NAME_FILTER % (name if name else '')))
        urls = [url]

        if name == "青香蕉下品(內銷)":
            urls[0] = urls[0].replace("status=4", "status=6").replace("青香蕉下品", "青香蕉")
        elif self.CONFIG.code == 'COG06' and name is None:
            urls.append((urls[0] + "青香蕉").replace("status=4", "status=6"))

        if name == "蒜頭(蒜球)(旬價)":
            urls[0] = urls[0].replace("status=4", "status=7").replace("蒜頭(蒜球)(旬價)", "蒜頭(蒜球)")
        elif self.CONFIG.code == 'COG05' and name is None:
            urls.append(urls[0].replace("status=4", "status=7") + "蒜頭(蒜球)")

        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(self.get, urls))

        return results

    def load(self, responses):
        data = []
        for response in responses:
            if response.text and '"DATASET":\n' not in response.text:
                try:
                    data_set = json.loads(response.text)
                    data_set = data_set.get('DATASET')
                    if re.search(r'status=(\d+)', response.url).group(1) == '7':
                        data_set = [_access_garlic_data_from_api(item) for item in data_set]
                    elif re.search(r'status=(\d+)', response.url).group(1) == '6':
                        data_set = list(map(lambda x: {**x, 'PRODUCTNAME': x['PRODUCTNAME'][:3] + '下品' + x['PRODUCTNAME'][3:]}, data_set))
                    data.extend(data_set)
                except Exception as e:
                    self.LOGGER.exception('%s \n%s' % (response.request.url, e), extra=self.LOGGER_EXTRA)

        # data should look like [D, B, {}, C, {}...] after loads
        if not data:
            return
        data_api = pd.DataFrame(data)
        data_api['AVGPRICE'] = data_api['AVGPRICE'].astype(float)
        data_api_avg = data_api[data_api['ORGNAME'] == '當日平均價']

        data_api = data_api[data_api['ORGNAME'] != '當日平均價']

        sources = self.SOURCE_QS.values_list('name', flat=True)
        products = self.PRODUCT_QS.values_list('code', flat=True)

        data_api['PRODUCTNAME'] = data_api['PRODUCTNAME'].str.strip()
        data_api['ORGNAME'] = data_api['ORGNAME'].str.strip()
        data_api = data_api[data_api['PRODUCTNAME'].isin(products)]
        data_api = data_api[data_api['ORGNAME'].isin(sources)]

        try:
            self._access_data_from_api(data_api)
        except Exception as e:
            self.LOGGER.exception(f'exception: {e}, response: {responses[0].text}', extra=self.LOGGER_EXTRA)

    def _access_data_from_api(self, data: pd.DataFrame):
        data_merge = self._compare_data_from_api_and_db(data)
        condition = (data_merge['avg_price_x'] != data_merge['avg_price_y'])
        if not data_merge[condition].empty:
            for _, value in data_merge[condition].fillna('').iterrows():
                try:
                    existed_tran = DailyTran.objects.get(id=int(value['id'] or 0))
                    if value['avg_price_x']:
                        self._update_data(value, existed_tran)
                    else:
                        existed_tran.delete()
                        self.LOGGER.warning(msg=f"The DailyTran data of the product: {value['product__code']} "
                                                f"on {value['date'].strftime('%Y-%m-%d')} "
                                                f"from source: {value['source__name']} with\n"
                                                f"avg_price: {value['avg_price_y']}\n has been deleted.")
                except Exception as e:
                    self._save_new_data(value)

    def _compare_data_from_api_and_db(self, data: pd.DataFrame):
        columns = {
            'AVGPRICE': 'avg_price',
            'ORGNAME': 'source__name',
            'PERIOD': 'date',
            'PRODUCTNAME': 'product__code',
        }
        data.rename(columns=columns, inplace=True)
        data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(x, '%Y/%m/%d').date())

        dailytran_qs = DailyTran.objects.filter(date=data['date'].iloc[0],
                                                product__type=self.TYPE,
                                                product__config=self.CONFIG)
        data_db = pd.DataFrame(list(dailytran_qs.values('id', 'avg_price', 'date', 'product__code', 'source__name'))) \
            if dailytran_qs else pd.DataFrame(columns=['id', 'avg_price', 'date', 'product__code', 'source__name'])

        return data.merge(data_db, on=['date', 'product__code', 'source__name'], how='outer')

    def _update_data(self, value, existed_tran):
        existed_tran.avg_price = value['avg_price_x']
        existed_tran.save()
        self.LOGGER.info(
            msg=f"The data of the product: {value['product__code']} on"
                f" {value['date'].strftime('%Y-%m-%d')} has been updated.")

    def _save_new_data(self, value):
        products = self.MODEL.objects.filter(code=value['product__code'])
        source = self.SOURCE_QS.get(name=value['source__name'])
        new_trans = [DailyTran(
            product=product,
            source=source,
            avg_price=value['avg_price_x'],
            date=value['date']
        ) for product in products]
        DailyTran.objects.bulk_create(new_trans)

