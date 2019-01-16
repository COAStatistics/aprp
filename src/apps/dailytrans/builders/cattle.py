from django.db.models import Q
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from apps.dailytrans.models import DailyTran


class Api(AbstractApi):

    # Settings
    API_NAME = 'cattle'
    ZFILL = True
    ROC_FORMAT = False
    SEP = '/'

    # Filters
    DATE_FILTER = '$filter=date+like+%s'
    CODE_FILTER = '$filter=item+like+%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_code = dic.get('item')
        product = self.PRODUCT_QS.filter(code=product_code).first()

        if product:
            tran = DailyTran(
                product=product,
                avg_price=dic.get('price'),
                date=date_transfer(sep=self.SEP, string=dic.get('date'), roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if not product:
                self.LOGGER.warning('Cannot Match Product: "%s" In Dictionary %s'
                                    % (product_code, dic), extra=self.LOGGER_EXTRA)
            return dic

    def request(self, date=None, code=None):
        url = self.API_URL
        if date and code:
            raise NotImplementedError('Do not support date and code advise as filter at one time!')
        if date:
            if not isinstance(date, datetime.date):
                raise NotImplementedError

            date_str = date_transfer(sep=self.SEP,
                                     date=date,
                                     roc_format=self.ROC_FORMAT,
                                     zfill=self.ZFILL)

            url = '&'.join((url, self.DATE_FILTER % date_str))

        if code:
            url = '&'.join((url, self.CODE_FILTER % code))

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
                    daily_tran_qs = DailyTran.objects.filter(Q(date__exact=obj.date)
                                                             & Q(product=obj.product))

                    if daily_tran_qs.count() > 1:
                        # log as duplicate
                        items = str(daily_tran_qs.values_list('id', flat=True))

                        self.LOGGER.warning('Find duplicate DailyTran item: %s' % items, extra=self.LOGGER_EXTRA)

                    elif daily_tran_qs.count() == 1:
                        daily_tran_qs.update(avg_price=obj.avg_price)
                    else:
                        if obj.avg_price > 0:
                            obj.save()

                except Exception as e:
                    self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
