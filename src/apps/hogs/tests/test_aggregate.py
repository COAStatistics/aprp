import datetime
from django.core.management import call_command
from django.test import TestCase
from apps.hogs.builder import direct
from apps.dailytrans.models import DailyTran
from django.db.models import Sum, F
from pandas import DataFrame


class AggregationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog08.yaml', verbosity=0)
        direct(start_date='2018/10/30', end_date='2018/10/31', format='%Y/%m/%d')

    def test_1031(self):
        qs = DailyTran.objects.filter(product__config__id=8,
                                      date=datetime.date(year=2018, month=10, day=31),
                                      source__enable=True)

        q = qs.values('source').annotate(
            avg_price=Sum(F('avg_price') * F('volume') * F('avg_weight')) / Sum(F('volume') * F('avg_weight')),
            sum_volume=Sum(F('volume')),
            avg_avg_weight=Sum(F('avg_weight') * F('volume')) / Sum(F('volume')),
        )

        q = q.values('source__name', 'avg_price', 'sum_volume', 'avg_avg_weight')
        d = DataFrame([i for i in q])
        d.to_csv('apps/hogs/tests/20181031.csv')
