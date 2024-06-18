from django.db.models import Q
import re
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from apps.dailytrans.models import DailyTran


class Api(AbstractApi):

    # Settings
    API_NAME = 'eir049'
    ZFILL = True
    ROC_FORMAT = False
    SEP = '/'

    # Filters
    START_DATE_FILTER = 'StartDate=%s'
    END_DATE_FILTER = 'EndDate=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):

        def create_tran(obj):
            if '公' in dic.get(obj.code):
                obj_male = self.PRODUCT_QS.get(code=f'{obj.code}公')
                obj_female = self.PRODUCT_QS.get(code=f'{obj.code}母')
                matches = re.findall(r'(?P<label>\w+)：(?P<value>\d+\.\d+)', dic.get(obj.code))
                prices = {}
                for label, value in matches:
                    prices[label] = float(value) / 0.6
                tran_male = DailyTran(
                    product=obj_male,
                    avg_price=prices['公'],
                    date=date_transfer(sep=self.SEP, string=dic.get('日期'), roc_format=self.ROC_FORMAT)
                )
                tran_female = DailyTran(
                    product=obj_female,
                    avg_price=prices['母'],
                    date=date_transfer(sep=self.SEP, string=dic.get('日期'), roc_format=self.ROC_FORMAT)
                )
                return [tran_male, tran_female]
            tran = DailyTran(
                product=obj,
                avg_price=float(dic.get(obj.code)) / 0.6,
                date=date_transfer(sep=self.SEP, string=dic.get('日期'), roc_format=self.ROC_FORMAT)
            )
            return [tran]

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        lst = []
        for obj in self.PRODUCT_QS.all():
            if obj.track_item and dic.get(obj.code):
                try:
                    trans = create_tran(obj)
                    lst.extend(trans)
                except Exception as e:
                    if '休市' in str(e) or '-' in str(e):
                        continue
                    else:
                        self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
        return lst

    def request(self, start_date=None, end_date=None):
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

        return self.get(url)

    def load(self, response):
        data = []
        if response.text:
            data = json.loads(response.text, object_hook=self.hook)
        # data should look like [[A,B,C], [A,B,C], ..] after loads
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
                            daily_tran_qs.update(avg_price=obj.avg_price)
                        else:
                            obj.save()

                    except Exception as e:
                        self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
