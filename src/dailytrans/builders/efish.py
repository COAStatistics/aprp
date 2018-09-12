from django.db.models import Q
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from dailytrans.models import DailyTran
from django.conf import settings


class Api(AbstractApi):

    # Settings
    API_NAME = 'efish'
    ZFILL = True
    ROC_FORMAT = True
    SEP = '.'

    # Filters
    START_DATE_FILTER = 'ds=%s'
    END_DATE_FILTER = 'de=%s'
    KEY_FILTER = 'tk=%s'
    CODE_FILTER = 'pid=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

        # Private Key, Please provide in settings/local.py
        try:
            self.API_URL = '&'.join((self.API_URL, self.KEY_FILTER % settings.EFISH_API_KEY))
        except AttributeError:
            raise NotImplementedError('efish API_KEY not specific in settings')

    def hook(self, dic):

        def create_tran(obj):
            code = obj.code
            tran = DailyTran(
                product=obj,
                avg_price=float(dic.get(code)),
                date=date_transfer(sep=self.SEP, string=dic.get('date'), roc_format=self.ROC_FORMAT)
            )
            return tran

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_code = dic.get('fishId')
        # It should get the right product "Origin" object, not "Wholesale"
        # Remember to provide type_id to Api initialization to limit PRODUCT_QS
        product = self.PRODUCT_QS.filter(code=product_code).first()
        if product:
            children = product.children()
            lst = []
            for child in children:
                try:
                    tran = create_tran(child)
                    lst.append(tran)
                except Exception as e:
                    self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
            return lst
        else:
            self.LOGGER.warning('Cannot Match Product: %s' % product_code, extra=self.LOGGER_EXTRA)
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

        if code:
            url = '&'.join((url, self.CODE_FILTER % code))

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

        return self.get(url, headers=headers, verify=False)

    def load(self, response):
        data = []
        if response.text:
            data = json.loads(response.text, object_hook=self.hook)

        # data should look like [[A,B,C], [A,B,C], ..] after loads
        for lst in data:
            for obj in lst:
                try:
                    if isinstance(obj, DailyTran):
                        # update if exists
                        daily_tran_qs = DailyTran.objects.filter(Q(date__exact=obj.date) &
                                                                 Q(product=obj.product))
                        if obj.source:
                            daily_tran_qs = daily_tran_qs.filter(source=obj.source)

                        if daily_tran_qs.count() > 1:
                            # log as duplicate
                            items = str(daily_tran_qs.values_list('id', flat=True))
                            self.LOGGER.warning('API Warning: Find duplicate DailyTran item: %s' % items, extra=self.LOGGER_EXTRA)

                        elif daily_tran_qs.count() == 1:
                            daily_tran_qs.update(avg_price=obj.avg_price)
                        else:
                            if obj.avg_price > 0:
                                obj.save()
                except Exception as e:
                    self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)

















