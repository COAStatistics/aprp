from django.db.models import Q
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from dailytrans.models import DailyTran


class Api(AbstractApi):

    # Settings
    API_NAME = 'eir107'
    ZFILL = True
    ROC_FORMAT = False
    SEP = '/'

    # Filters
    TRANS_DATE_FILTER = 'transDate+like+%s'
    SOURCE_FILTER = 'shortName+like+%s'
    CODE_FILTER = 'productID+like+%s'

    # Logger
    LOGGER_EXTRA = {
        'type_code': 'LOT-rams',
    }

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_code = dic.get('productID')
        product = self.PRODUCT_QS.filter(code=product_code).first()
        source_name = dic.get('shortName')
        source = self.SOURCE_QS.filter_by_name(source_name).first()
        if product and source:
            tran = DailyTran(
                product=product,
                source=source,
                avg_price=dic.get('avgPrice'),
                avg_weight=dic.get('avgWeight'),
                volume=dic.get('quantity'),
                date=date_transfer(sep=self.SEP, string=dic.get('transDate'), roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if not product:
                self.LOGGER.warning('Cannot Match Product: "%s" In Dictionary %s'
                                    % (product_code, dic), extra=self.LOGGER_EXTRA)
            if not source:
                self.LOGGER.warning('Cannot Match Source: "%s" In Dictionary %s'
                                    % (source_name, dic), extra=self.LOGGER_EXTRA)
            return dic

    def request(self, date=None, source=None, code=None):

        def dispatch(start):
            if not start:
                return '$filter='
            else:
                return '+and+'

        start = False
        url = self.API_URL
        if date:
            if not isinstance(date, datetime.date):
                raise NotImplementedError

            date = date_transfer(sep=self.SEP,
                                 date=date,
                                 roc_format=self.ROC_FORMAT,
                                 zfill=self.ZFILL)
            s = dispatch(start)
            url = s.join((url, self.TRANS_DATE_FILTER % date))

            if not start:
                start = True

        if source:
            s = dispatch(start)
            url = s.join((url, self.SOURCE_FILTER % source))

            if not start:
                start = True

        if code:
            s = dispatch(start)
            url = s.join((url, self.CODE_FILTER % code))

        return self.get(url)

    def load(self, response):
        data = []
        if response.text:
            data = json.loads(response.text, object_hook=self.hook)
        # data should look like [D, B, {}, C, {}...] after loads
        for obj in data:
            if isinstance(obj, DailyTran):
                try:
                    # update if exists
                    daily_tran_qs = DailyTran.objects.filter(Q(date__exact=obj.date) &
                                                             Q(product=obj.product))
                    if obj.source:
                        daily_tran_qs = daily_tran_qs.filter(source=obj.source)

                    if daily_tran_qs.count() > 1:
                        # log as duplicate
                        items = str(daily_tran_qs.values_list('id', flat=True))
                        self.LOGGER.warning('Find duplicate DailyTran item: %s' % items,
                                           extra=self.LOGGER_EXTRA)

                    elif daily_tran_qs.count() == 1:
                        daily_tran_qs.update(avg_weight=obj.avg_weight,
                                             avg_price=obj.avg_price,
                                             volume=obj.volume)
                    else:
                        obj.save()
                except Exception as e:
                    self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
















