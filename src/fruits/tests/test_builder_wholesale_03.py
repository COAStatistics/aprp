import datetime
from django.core.management import call_command
from django.test import TestCase
from fruits.builder import direct_wholesale_03
from dailytrans.models import DailyTran
from fruits.models import Fruit
from configs.models import Source
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog03.yaml', verbosity=0)

        self.start_date = datetime.date(year=2018, month=3, day=6)
        self.end_date = datetime.date(year=2018, month=3, day=6)

    def test_direct_single(self):
        result = direct_wholesale_03(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result.success)

        obj = Fruit.objects.filter(code='I', track_item=True).first()

        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 3)

    def test_direct_multi(self):
        result = direct_wholesale_03(start_date='2018/02/07', end_date='2018/2/10', format='%Y/%m/%d')
        self.assertTrue(result.success)

        start_date = datetime.date(year=2018, month=2, day=7)
        end_date = datetime.date(year=2018, month=2, day=10)
        obj_ids = Fruit.objects.filter(Q(code='I') | Q(code='O')).values('id')
        sources = Source.objects.filter(Q(name__exact='臺北二') | Q(name__exact='板橋區'))

        qs = DailyTran.objects.filter(product__id__in=obj_ids,
                                      source__in=sources,
                                      date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 12)

