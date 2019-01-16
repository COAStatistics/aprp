from django.db.models import Q
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from apps.dailytrans.models import DailyTran


class Api(AbstractApi):

    # Settings
    API_NAME = 'eir030'
    ZFILL = True
    ROC_FORMAT = True
    SEP = '.'

    # Filters
    START_DATE_FILTER = 'StartDate=%s'
    END_DATE_FILTER = 'EndDate=%s'
    SOURCE_FILTER = 'Market=%s'
    CODE_FILTER = 'CropCode=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):
        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_code = dic.get('作物代號')
        products = self.PRODUCT_QS.filter(code=product_code).all()
        source_name = dic.get('市場名稱')
        source = self.SOURCE_QS.filter_by_name(source_name).first()
        if products and source:
            trans = [
                DailyTran(
                    product=p,
                    source=source,
                    up_price=dic.get('上價'),
                    mid_price=dic.get('中價'),
                    low_price=dic.get('下價'),
                    avg_price=dic.get('平均價'),
                    volume=dic.get('交易量'),
                    date=date_transfer(sep=self.SEP, string=dic.get('交易日期'), roc_format=self.ROC_FORMAT)
                ) for p in products
            ]
            return trans
        else:
            if not products:
                self.LOGGER.warning('Cannot Match Product: "%s" In Dictionary %s'
                                    % (product_code, dic), extra=self.LOGGER_EXTRA)
            if not source:
                self.LOGGER.warning('Cannot Match Source: "%s" In Dictionary %s'
                                    % (source_name, dic), extra=self.LOGGER_EXTRA)
            return dic

    def request(self, start_date=None, end_date=None, source=None, code=None):
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

        return self.get(url)

    def load(self, response):
        data = []
        if response.text:
            data = json.loads(response.text, object_hook=self.hook)

        # data should look like [[D, R], [B], {}, [C, A], {}...] after loads
        data = [obj for obj in data if isinstance(obj, list)]
        for lst in data:
            for obj in lst:
                if isinstance(obj, DailyTran):
                    try:
                        # update if exists
                        daily_tran_qs = DailyTran.objects.filter(Q(date__exact=obj.date)
                                                                 & Q(product=obj.product))
                        if obj.source:
                            daily_tran_qs = daily_tran_qs.filter(source=obj.source)

                        if daily_tran_qs.count() > 1:
                            # log as duplicate
                            items = str(daily_tran_qs.values_list('id', flat=True))
                            self.LOGGER.warning('Find duplicate DailyTran item: %s' % items, extra=self.LOGGER_EXTRA)

                        elif daily_tran_qs.count() == 1:
                            daily_tran_qs.update(up_price=obj.up_price,
                                                 mid_price=obj.mid_price,
                                                 low_price=obj.low_price,
                                                 avg_price=obj.avg_price,
                                                 volume=obj.volume)
                        else:
                            if obj.avg_price > 0 and obj.volume > 0:
                                obj.save()

                    except Exception as e:
                        self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
