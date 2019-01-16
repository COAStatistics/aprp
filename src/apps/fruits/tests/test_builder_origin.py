import datetime
from django.core.management import call_command
from django.test import TestCase
from apps.fruits.builder import direct_origin
from apps.dailytrans.models import DailyTran
from apps.fruits.models import Fruit
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog06-test.yaml', verbosity=0)

        self.start_date = datetime.date(year=2017, month=9, day=1)
        self.end_date = datetime.date(year=2017, month=9, day=3)

    def test_direct_single(self):
        direct_origin(start_date=self.start_date, end_date=self.end_date)
        obj = Fruit.objects.filter(code='文旦').first()

        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 9)

    def test_direct_multi(self):
        start_date = datetime.date(year=2017, month=4, day=1)
        end_date = datetime.date(year=2017, month=9, day=1)
        direct_origin(start_date=start_date, end_date=end_date)
        obj_ids = Fruit.objects.filter(Q(code='文旦') | Q(code='青梅(竿採)')).values('id')

        qs = DailyTran.objects.filter(product__id__in=obj_ids,
                                      date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 64)
