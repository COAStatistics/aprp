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

    # hook is stopped using
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
        """
        For adding parameters in url.
        """
        url = self.API_URL
        
        # 取得農產品名稱(如果有)
        name = kwargs.get('name') if kwargs.get('name') else None
        
        # 設定日期範圍
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
        """
        Load data from the API response.

        Parameters
        ----------
        responses : list
            list of requests.Response objects.

        Returns
        -------
        None
        """
        data = []
        for response in responses:
            try:
                # load data
                data_set = response.json()
                data_set = data_set.get('DATASET')
                # handle special cases
                if re.search(r'status=(\d+)', response.url).group(1) == '7':
                    # handle "status=7" case
                    data_set = [_access_garlic_data_from_api(item) for item in data_set]
                elif re.search(r'status=(\d+)', response.url).group(1) == '6':
                    # handle "status=6" case
                    data_set = list(map(lambda x: {**x, 'PRODUCTNAME': x['PRODUCTNAME'][:3] + '下品' + x['PRODUCTNAME'][3:]}, data_set))
                data.extend(data_set)
            except Exception as e:
                if len(response.text) == 0:
                    self.LOGGER.warning(f'no data returned\nurl={response.request.url}', extra=self.LOGGER_EXTRA)
                else:
                    self.LOGGER.exception(
                        f'resp={response.text}\nurl={response.request.url}\nexc={e}',
                        extra=self.LOGGER_EXTRA
                    )

        # data should look like [D, B, {}, C, {}...] after loads
        if not data:
            return
        # convert data to pandas DataFrame
        data_api = pd.DataFrame(data)
        data_api['AVGPRICE'] = data_api['AVGPRICE'].astype(float)
        data_api_avg = data_api[data_api['ORGNAME'] == '當日平均價']

        data_api = data_api[data_api['ORGNAME'] != '當日平均價']

        # filter data by source and product
        sources = self.SOURCE_QS.values_list('name', flat=True)
        products = self.PRODUCT_QS.values_list('code', flat=True)

        data_api['PRODUCTNAME'] = data_api['PRODUCTNAME'].str.strip()
        data_api['ORGNAME'] = data_api['ORGNAME'].str.strip()
        data_api = data_api[data_api['PRODUCTNAME'].isin(products)]
        data_api = data_api[data_api['ORGNAME'].isin(sources)]

        try:
            self._access_data_from_api(data_api)
        except Exception as e:
            self.LOGGER.exception(f'exception: {e}, data_api: {data_api}', extra=self.LOGGER_EXTRA)

    def _access_data_from_api(self, data: pd.DataFrame):
        """
        Compare data from API with data in DB and update or delete records accordingly.
        """
        # merge data from API with data in DB
        data_merge = self._compare_data_from_api_and_db(data)

        # filter out records that need to be updated or deleted
        # due to merge two data with date, product id and source id, there are two average prices data that are from
        # Api and DB respectively, we can compare these two and decide whether we should update or delete.
        condition = (data_merge['avg_price_x'] != data_merge['avg_price_y'])
        if not data_merge[condition].empty:
            for _, value in data_merge[condition].fillna('').iterrows():
                try:
                    # get the existed DailyTran record
                    existed_tran = DailyTran.objects.get(id=int(value['id'] or 0))

                    if value['avg_price_x']:
                        # if the avg_price in API is not None, update the existed record
                        self._update_data(value, existed_tran)
                    else:
                        # if the avg_price in API is None, delete the existed record
                        existed_tran.delete()
                        self.LOGGER.warning(msg=f"The DailyTran data of the product: {value['product__code']} "
                                                f"on {value['date'].strftime('%Y-%m-%d')} "
                                                f"from source: {value['source__name']} with\n"
                                                f"avg_price: {value['avg_price_y']}\n has been deleted.")
                except Exception as e:
                    # if no existed record is found, save the data as a new record
                    self._save_new_data(value)

    def _compare_data_from_api_and_db(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compare data from API with data in DB and return a merged DataFrame.

        The DataFrame is merged on columns 'date', 'product__code', and 'source__name'.
        The columns 'id', 'avg_price' are added from the DB data.
        The columns 'avg_price_x' and 'avg_price_y' are added from the API and DB data.
        The 'avg_price_x' is the value from API, and 'avg_price_y' is the value from DB.
        :param data: DataFrame: data from API
        :return: DataFrame: merged DataFrame
        """
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
        """
        Update the data in DB with the data from API.

        :param value: dict: data from API
        :param existed_tran: DailyTran: the existed record in DB
        """
        # update the existed record with the new data
        # the avg_price_x is the value from API, it's newer than the value in DB
        existed_tran.avg_price = value['avg_price_x']
        existed_tran.save()
        self.LOGGER.info(
            msg=f"The data of the product: {value['product__code']} on"
                f" {value['date'].strftime('%Y-%m-%d')} has been updated.")

    def _save_new_data(self, value):
        """
        Save the data in DB.

        :param value: dict: data from API
        """
        # get the products from DB
        products = self.MODEL.objects.filter(code=value['product__code'])
        # get the source from DB
        source = self.SOURCE_QS.get(name=value['source__name'])
        # create a list of new records
        new_trans = [DailyTran(
            # set the product
            product=product,
            # set the source
            source=source,
            # set the average price
            avg_price=value['avg_price_x'],
            # set the date
            date=value['date']
        ) for product in products]
        # bulk create the new records
        DailyTran.objects.bulk_create(new_trans)

