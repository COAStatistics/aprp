from django.db.models import Q
import datetime
import json
from xml.etree import ElementTree
from .utils import date_transfer
from .abstract import AbstractApi
from apps.dailytrans.models import DailyTran


class Api(AbstractApi):
    """
    Note: This Api Access Grand Total Trans Data Across App Crop, Fruits, Flower
    Custom Attributes: market_type, sum_to_product
    """
    # Settings
    API_NAME = 'amis'
    ZFILL = True
    ROC_FORMAT = True
    SEP = ''

    # Filters
    DATE_FILTER = 'transDate=%s'
    SOURCE_FILTER = 'marketNo=%s'

    def __init__(self, model, config_code, type_id, logger_type_code=None, market_type=None, sum_to_product=None):
        """
        :param market_type: V=crops, F=fruits, L=flowers
        :param sum_to_product: provide product code and get average price/volume for all detail objects in api result
        """
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)
        if not isinstance(market_type, str):
            raise NotImplementedError
        else:
            self.API_URL = '&'.join((self.API_URL, 'marketType=%s' % market_type))

        self.sum_to_product = sum_to_product

    def hook(self, dic):
        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        source_code = dic.get('MarketNo')
        source = self.SOURCE_QS.filter(code=source_code).first()
        date = date_transfer(sep=self.SEP, string=dic.get('TransDate'), roc_format=self.ROC_FORMAT)
        products = dic.get('Detail')
        if source and products:
            trans = []
            # sum detail object and translate to "one" DailyTran
            if self.sum_to_product:

                def sum_details(lst):
                    sum_avg_price = 0
                    sum_volume = 0
                    for dic in lst:
                        #排除ProductNo含有'-' 之子項,僅用平等之大項進行全部花卉L之計算,例如排除 FH-FH201~ FH-FH204
                        if '-' not in dic.get('ProductNo'):
                            avg_price = float(dic.get('AvgPrice'))
                            volume = float(dic.get('TransVolume'))
                            sum_avg_price += avg_price * volume
                            sum_volume += volume
                    return sum_avg_price / sum_volume, sum_volume

                product_code = self.sum_to_product
                product = self.PRODUCT_QS.filter(code=product_code).first()
                if product:
                    avg_price, sum_volume = sum_details(products)
                    tran = DailyTran(
                        product=product,
                        source=source,
                        avg_price=avg_price,
                        volume=sum_volume,
                        date=date,
                    )
                    trans.append(tran)
                else:
                    self.LOGGER.warning(
                        'Cannot Match Product: "%s" In Dictionary %s'
                        % (product_code, dic), extra=self.LOGGER_EXTRA)

            else:
                # translate detail objects to "multi" DailyTran
                for dic in products:
                    product_code = dic.get('ProductNo')
                    product = self.PRODUCT_QS.filter(code=product_code).first()
                    if product:
                        tran = DailyTran(
                            product=product,
                            source=source,
                            avg_price=float(dic.get('AvgPrice')),
                            volume=float(dic.get('TransVolume')),
                            date=date,
                        )
                        trans.append(tran)
                    else:
                        self.LOGGER.warning(
                            'Cannot Match Product: "%s" In Dictionary %s'
                            % (product_code, dic), extra=self.LOGGER_EXTRA)

            return trans

        if products and not source:
            self.LOGGER.warning('Cannot Match Source: "%s" In Dictionary %s'
                                % (source_code, dic), extra=self.LOGGER_EXTRA)
            return dic

        else:
            return dic

    def request(self, date=None, source=None):
        url = self.API_URL

        if date:
            if not isinstance(date, datetime.date):
                raise NotImplementedError

            date_str = date_transfer(sep=self.SEP,
                                     date=date,
                                     roc_format=self.ROC_FORMAT,
                                     zfill=self.ZFILL)

            url = '&'.join((url, self.DATE_FILTER % date_str))

        if not source:
            source = 'ALL'
        url = '&'.join((url, self.SOURCE_FILTER % source))

        response = self.get(url)
        tree = ElementTree.fromstring(response.content)

        return tree

    def load(self, response):
        data = []
        if response.text:
            data_set = json.loads(response.text, object_hook=self.hook)
            data = data_set['DayTransInfo']

        if data:
            # data should look like [[A, B, C], [D, E], {}, [F], {}...] after loads
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
                                self.LOGGER.warning('Find duplicate DailyTran item: %s' % items,
                                                    extra=self.LOGGER_EXTRA)

                            elif daily_tran_qs.count() == 1:
                                daily_tran_qs.update(avg_price=obj.avg_price,
                                                     volume=obj.volume)
                            else:
                                if obj.avg_price > 0:
                                    obj.save()

                        except Exception as e:
                            self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
