import datetime
from django.core.management import call_command
from django.test import TestCase
from gooses.builder import direct
from dailytrans.models import DailyTran
from gooses.models import Goose
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog12.yaml', verbosity=0)

        self.start_date = datetime.date(year=2017, month=1, day=1)
        self.end_date = datetime.date(year=2017, month=1, day=3)

    def test_direct_single(self):
        direct(start_date=self.start_date, end_date=self.end_date)
        obj = Goose.objects.filter(code='肉鵝(上鵝)價格/土鵝').first()

        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 3)

    def test_direct_multi(self):
        start_date = datetime.date(year=2017, month=1, day=1)
        end_date = datetime.date(year=2017, month=1, day=10)
        direct(start_date='2017/01/01', end_date='2017/01/10', format='%Y/%m/%d')
        obj_ids = Goose.objects.filter(Q(code='肉鵝(上鵝)價格/土鵝') | Q(code='小鵝產地價格(隻)/土鵝')).values('id')

        qs = DailyTran.objects.filter(product__id__in=obj_ids,
                                      date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 2*10)

    def test_direct_all(self):
        start_date = datetime.date(year=2017, month=1, day=1)
        end_date = datetime.date(year=2017, month=1, day=5)
        direct(start_date='2017/01/01', end_date='2017/01/5', format='%Y/%m/%d')

        qs = DailyTran.objects.filter(date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 4*5)

    def test_direct_format(self):
        direct(start_date=self.start_date, end_date=self.end_date)
        obj = Goose.objects.filter(code='肉鵝(上鵝)價格/土鵝').first()

        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 3)
