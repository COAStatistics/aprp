import datetime
from django.core.management import call_command
from django.test import TestCase
from chickens.builder import direct
from dailytrans.models import DailyTran
from chickens.models import Chicken
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog10.yaml', verbosity=0)

        self.start_date = datetime.date(year=2018, month=4, day=25)
        self.end_date = datetime.date(year=2018, month=5, day=2)

    def test_direct_single(self):
        direct(start_date=self.start_date, end_date=self.end_date)
        obj = Chicken.objects.filter(code='紅羽土雞北區').first()

        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 8)

    def test_direct_multi(self):
        start_date = datetime.date(year=2017, month=1, day=1)
        end_date = datetime.date(year=2017, month=1, day=10)
        direct(start_date='2017/01/01', end_date='2017/01/10', format='%Y/%m/%d')
        obj_ids = Chicken.objects.filter(Q(code='紅羽土雞北區') | Q(code='紅羽土雞南區')).values('id')

        qs = DailyTran.objects.filter(product__id__in=obj_ids,
                                      date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 20)

    def test_direct_all(self):
        start_date = datetime.date(year=2017, month=1, day=1)
        end_date = datetime.date(year=2017, month=1, day=5)
        direct(start_date='2017/01/01', end_date='2017/01/5', format='%Y/%m/%d')

        qs = DailyTran.objects.filter(date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 8*5)

    def test_direct_format(self):
        direct(start_date=self.start_date, end_date=self.end_date)
        obj = Chicken.objects.filter(code='紅羽土雞北區').first()

        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 8)
