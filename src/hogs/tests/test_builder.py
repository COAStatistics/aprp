import datetime
from django.core.management import call_command
from django.test import TestCase
from hogs.builder import direct
from dailytrans.models import DailyTran
from hogs.models import Hog
from configs.models import Source
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog08.yaml', verbosity=0)

        self.start_date = datetime.date(year=2018, month=1, day=3)
        self.end_date = datetime.date(year=2018, month=1, day=4)

    def test_direct_single(self):
        result = direct(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result.success)
        obj = Hog.objects.filter(code='規格豬(75公斤以上)').first()
        sources = Source.objects.filter(Q(name__exact='臺南市') | Q(name__exact='花蓮縣'))
        self.assertTrue(sources.count(), 4)
        qs = DailyTran.objects.filter(product=obj,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 4)

    def test_direct_multi(self):
        direct(start_date='2018/01/03', end_date='2018/01/04', format='%Y/%m/%d')

        qs = DailyTran.objects.filter(date__range=(self.start_date, self.end_date))

        self.assertEquals(qs.count(), 97)
