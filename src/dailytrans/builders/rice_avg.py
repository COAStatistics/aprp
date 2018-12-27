from django.db.models import Q
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from dailytrans.models import DailyTran


class Api(AbstractApi):

    # Settings
    API_NAME = 'rice_avg'
    ZFILL = True
    ROC_FORMAT = True
    SEP = '.'

    # Filters
    START_DATE_FILTER = 'StartDate=%s'
    END_DATE_FILTER = 'EndDate=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):

        def create_tran(obj):
            tran = DailyTran(
                product=obj,
                avg_price=dic.get(obj.code),
                date=date_transfer(sep=self.SEP, string=dic.get('pt_date'), roc_format=self.ROC_FORMAT)
            )

            # NOTE: wholesale obj price need to division by 100
            if obj.code in ['pt_2japt', 'pt_2tsait', 'pt_2sangt', 'pt_2glutrt', 'pt_2glutlt',
                            'pt_4japt', 'pt_4tsait', 'pt_4sangt', 'pt_4glutrt', 'pt_4glutlt']:
                tran.avg_price = tran.avg_price / 100

            return tran

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        lst = []
        for obj in self.PRODUCT_QS.all():
            if obj.track_item and dic.get(obj.code):
                tran = create_tran(obj)
                lst.append(tran)

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
