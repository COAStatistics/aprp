import pandas as pd
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from apps.dailytrans.models import DailyTran


class Api(AbstractApi):
    # Settings
    API_NAME = 'eir032'
    ZFILL = True
    ROC_FORMAT = True
    SEP = ''

    # Filters
    START_DATE_FILTER = 'StartDate=%s'
    END_DATE_FILTER = 'EndDate=%s'
    SOURCE_FILTER = 'MarketName=%s'
    CODE_FILTER = 'TypeNo=%s'
    NAME_FILTER = 'TypeName=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_code = dic.get('品種代碼')
        product = self.PRODUCT_QS.filter(code=product_code).first()
        source_name = dic.get('市場名稱')
        source = self.SOURCE_QS.filter_by_name(source_name).first()
        if product and source:
            tran = DailyTran(
                product=product,
                source=source,
                up_price=dic.get('上價'),
                mid_price=dic.get('中價'),
                low_price=dic.get('下價'),
                avg_price=dic.get('平均價'),
                volume=dic.get('交易量'),
                date=date_transfer(sep=self.SEP, string=dic.get('交易日期'), roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if not product and dic.get('魚貨名稱') != "休市":
                self.LOGGER.warning('Cannot Match Product: "%s" In Dictionary %s'
                                    % (product_code, dic), extra=self.LOGGER_EXTRA)
            if not source:
                self.LOGGER.warning('Cannot Match Source: "%s" In Dictionary %s'
                                    % (source_name, dic), extra=self.LOGGER_EXTRA)
            return dic

    def request(self, start_date=None, end_date=None, source=None, code=None, name=None):
        url = self.API_URL
        if start_date:
            if not isinstance(start_date, datetime.date):
                raise NotImplementedError

            start_date_str = date_transfer(sep=self.SEP,
                                           date=start_date,
                                           roc_format=self.ROC_FORMAT,
                                           zfill=self.ZFILL)

            url = '&'.join((url, self.START_DATE_FILTER % start_date_str))

        if end_date:
            if not isinstance(end_date, datetime.date):
                raise NotImplementedError

            end_date_str = date_transfer(sep=self.SEP,
                                         date=end_date,
                                         roc_format=self.ROC_FORMAT,
                                         zfill=self.ZFILL)

            url = '&'.join((url, self.END_DATE_FILTER % end_date_str))

        if start_date and end_date:
            if start_date > end_date:
                raise AttributeError

        if source:
            url = '&'.join((url, self.SOURCE_FILTER % source))

        if code:
            url = '&'.join((url, self.CODE_FILTER % code))

        if name:
            url = '&'.join((url, self.NAME_FILTER % name))

        return self.get(url)

    def load(self, response):
        data = []
        if response.text:
            try:
                data = json.loads(response.text)
            except Exception as e:
                self.LOGGER.exception(f'exception: {e}, response: {response.text}', extra=self.LOGGER_EXTRA)

        if not data:
            return

        data = pd.DataFrame(data,
                            columns=['上價', '中價', '下價', '平均價', '交易量', '交易日期', '品種代碼', '市場名稱',
                                     '魚貨名稱'])
        data = data[data['品種代碼'].isin(self.target_items)]
        try:
            self._access_data_from_api(data)
        except Exception as e:
            self.LOGGER.exception(f'exception: {e}, response: {response.text}', extra=self.LOGGER_EXTRA)

    def _access_data_from_api(self, data: pd.DataFrame):
        data_merge = self._compare_data_from_api_and_db(data)
        condition = ((data_merge['avg_price_x'] != data_merge['avg_price_y']) | (
                            data_merge['up_price_x'] != data_merge['up_price_y']) | (
                            data_merge['low_price_x'] != data_merge['low_price_y']) | (
                            data_merge['mid_price_x'] != data_merge['mid_price_y']) | (
                            data_merge['volume_x'] != data_merge['volume_y']))
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
                                                f"up_price: {value['up_price_y']}\n"
                                                f"mid_price: {value['mid_price_y']}\n"
                                                f"low_price: {value['low_price_y']}\n"
                                                f"avg_price: {value['avg_price_y']}\n"
                                                f"volume: {value['volume_y']} has been deleted.")
                except Exception as e:
                    self._save_new_data(value)

    def _compare_data_from_api_and_db(self, data: pd.DataFrame):
        columns = {
            '上價': 'up_price',
            '中價': 'mid_price',
            '下價': 'low_price',
            '平均價': 'avg_price',
            '交易量': 'volume',
            '品種代碼': 'product__code',
            '市場名稱': 'source__name',
            '交易日期': 'date',
            '魚貨名稱': 'product__name'
        }
        data.rename(columns=columns, inplace=True)
        data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(
            f'{int(x) // 10000 + 1911}-{(int(x) // 100) % 100:02d}-{int(x) % 100:02d}', '%Y-%m-%d').date())
        data['source__name'] = data['source__name'].str.replace('台', '臺')
        data['product__code'] = data['product__code'].astype(str)

        data_db = DailyTran.objects.filter(date=data['date'].iloc[0], product__type=1, product__config=self.CONFIG)
        data_db = pd.DataFrame(list(data_db.values('id', 'product__id', 'product__code', 'up_price', 'mid_price',
                                                   'low_price', 'avg_price', 'volume', 'date', 'source__name'))) \
            if data_db else pd.DataFrame(columns=['id', 'product__id', 'product__code', 'up_price', 'mid_price',
                                                  'low_price', 'avg_price', 'volume', 'date', 'source__name'])

        return data.merge(data_db, on=['date', 'product__code', 'source__name'], how='outer')

    def _update_data(self, value, existed_tran):
        existed_tran.up_price = value['up_price_x']
        existed_tran.mid_price = value['mid_price_x']
        existed_tran.low_price = value['low_price_x']
        existed_tran.avg_price = value['avg_price_x']
        existed_tran.volume = value['volume_x']
        existed_tran.save()
        self.LOGGER.info(
            msg=f"The data of the product: {value['product__code']} on"
                f" {value['date'].strftime('%Y-%m-%d')} has been updated.")

    def _save_new_data(self, value):
        products = self.MODEL.objects.filter(code=value['product__code'])
        source = self.SOURCE_QS.filter_by_name(value['source__name']).first()
        new_trans = [DailyTran(
            product=product,
            source=source,
            up_price=value['up_price_x'],
            mid_price=value['mid_price_x'],
            low_price=value['low_price_x'],
            avg_price=value['avg_price_x'],
            volume=value['volume_x'],
            date=value['date']
        ) for product in products]
        DailyTran.objects.bulk_create(new_trans)

        # # data should look like [D, B, {}, C, {}...] after loads
        # for obj in data:
        #     if isinstance(obj, DailyTran):
        #         try:
        #             # update if exists
        #             daily_tran_qs = DailyTran.objects.filter(Q(date__exact=obj.date)
        #                                                      & Q(product=obj.product))
        #             if obj.source:
        #                 daily_tran_qs = daily_tran_qs.filter(source=obj.source)
        #
        #             if daily_tran_qs.count() > 1:
        #                 # log as duplicate
        #                 items = str(daily_tran_qs.values_list('id', flat=True))
        #
        #                 self.LOGGER.warning('Find duplicate DailyTran item: %s' % items, extra=self.LOGGER_EXTRA)
        #
        #             elif daily_tran_qs.count() == 1:
        #                 daily_tran_qs.update(up_price=obj.up_price,
        #                                      mid_price=obj.mid_price,
        #                                      low_price=obj.low_price,
        #                                      avg_price=obj.avg_price,
        #                                      volume=obj.volume)
        #             else:
        #                 if obj.avg_price > 0 and obj.volume > 0:
        #                     obj.save()
        #
        #         except Exception as e:
        #             self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
