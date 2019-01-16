import datetime
from django.core.management import call_command
from django.test import TestCase
from apps.seafoods.builder import direct_wholesale
from apps.dailytrans.models import DailyTran
from apps.seafoods.models import Seafood
from apps.configs.models import Source
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog13-test.yaml', verbosity=0)

        self.start_date = datetime.date(year=2017, month=1, day=3)
        self.end_date = datetime.date(year=2017, month=1, day=3)

    def test_direct_single(self):
        result = direct_wholesale(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result.success)
        obj = Seafood.objects.filter(code='1012').first()
        self.assertIsNotNone(obj)
        sources = Source.objects.filter(Q(name__exact='臺中') | Q(name__exact='新竹'))

        qs = DailyTran.objects.filter(product=obj,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 2)

    def test_direct_multi(self):
        start_date = datetime.date(year=2017, month=1, day=1)
        end_date = datetime.date(year=2017, month=1, day=10)
        direct_wholesale(start_date='2017/01/01', end_date='2017/01/10', format='%Y/%m/%d')
        crop_ids = Seafood.objects.filter(Q(code='1012') | Q(code='1011')).values('id')
        sources = Source.objects.filter(Q(name__exact='臺中') | Q(name__exact='新竹'))

        qs = DailyTran.objects.filter(product__id__in=crop_ids,
                                      source__in=sources,
                                      date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 31)
