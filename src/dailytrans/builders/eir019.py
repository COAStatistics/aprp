from django.db.models import Q
import datetime
import json
import math
from .utils import date_transfer
from .abstract import AbstractApi
from dailytrans.models import DailyTran


class Api(AbstractApi):

    # Settings
    API_NAME = 'eir019'
    ZFILL = True
    ROC_FORMAT = True
    SEP = ''

    # Filters
    TRANS_DATE_FILTER = 'TransDate=%s'
    SOURCE_FILTER = 'MarketName=%s'

    # Column Names
    VOLUME_COLUMN = '頭數'
    AVG_WEIGHT_COLUMN = '平均重量'
    AVG_PRICE_COLUMN = '平均價格'
    COLUMN_SEP = '-'

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):

        def create_tran(obj, source):
            code = obj.code
            volume_column = self.COLUMN_SEP.join((code, self.VOLUME_COLUMN))
            avg_weight_column = self.COLUMN_SEP.join((code, self.AVG_WEIGHT_COLUMN))
            avg_price_column = self.COLUMN_SEP.join((code, self.AVG_PRICE_COLUMN))
            tran = DailyTran(
                product=obj,
                source=source,
                volume=dic.get(volume_column),
                avg_weight=dic.get(avg_weight_column),
                avg_price=round(float(dic.get(avg_price_column)), 1),
                date=date_transfer(sep=self.SEP, string=dic.get('交易日期'), roc_format=True)
            )

            return tran

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        source_name = dic.get('市場名稱')
        if source_name:
            source_name = source_name.strip()
        source = self.SOURCE_QS.filter_by_name(source_name).first()

        if source:
            lst = []
            for obj in self.PRODUCT_QS.all():
                if obj.track_item:
                    try:
                        tran = create_tran(obj, source)
                        lst.append(tran)
                    except Exception as e:
                        self.LOGGER.exception("Parsing Error: %s" % dic, extra=self.LOGGER_EXTRA)
            return lst
        else:
            # log as cannot find source item
            self.LOGGER.warning('Cannot Match Source: "%s" In Dictionary %s'
                                % (source_name, dic), extra=self.LOGGER_EXTRA)
            return dic

    def request(self, date, source=None):
        url = self.API_URL

        if date:
            if not isinstance(date, datetime.date):
                raise NotImplementedError

            date = date_transfer(sep=self.SEP,
                                 date=date,
                                 roc_format=self.ROC_FORMAT,
                                 zfill=self.ZFILL)

            url = '&'.join((url, self.TRANS_DATE_FILTER % date))

        if source:
            url = '&'.join((url, self.SOURCE_FILTER % source))

        return self.get(url)

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
                            self.LOGGER.warning('Find duplicate DailyTran item: %s' % items, extra=self.LOGGER_EXTRA)

                        elif daily_tran_qs.count() == 1:
                            daily_tran_qs.update(avg_price=obj.avg_price,
                                                 volume=obj.volume,
                                                 avg_weight=obj.avg_weight)
                        else:
                            if obj.volume > 0 and obj.avg_price > 0 and obj.avg_weight > 0:
                                obj.save()
                            elif not math.isclose(obj.volume + obj.avg_price + obj.avg_weight, 0):
                                self.LOGGER.warning('Find not valid hog DailyTran item: %s' % str(obj), extra=self.LOGGER_EXTRA)
                except Exception as e:
                    self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)















