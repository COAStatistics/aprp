import datetime
from django.core.management import call_command
from django.test import TestCase
from crops.builder import direct_wholesale_05
from dailytrans.models import DailyTran
from crops.models import Crop
from configs.models import Source
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog05-test.yaml', verbosity=0)

        self.start_date = datetime.date(year=2017, month=1, day=1)
        self.end_date = datetime.date(year=2017, month=1, day=3)

    def test_direct_single(self):
        direct_wholesale_05(start_date=self.start_date, end_date=self.end_date)
        crop = Crop.objects.filter(code='LA1').first()
        sources = Source.objects.filter(Q(name__exact='臺北一') | Q(name__exact='臺北二'))

        qs = DailyTran.objects.filter(product=crop,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 4)

    def test_direct_multi(self):
        direct_wholesale_05(start_date='2017/01/01', end_date='2017/01/10', format='%Y/%m/%d')
        crop_ids = Crop.objects.filter(Q(code='LA1') | Q(code='LA2')).values('id')
        sources = Source.objects.filter(Q(name__exact='臺北一') | Q(name__exact='臺北二'))

        qs = DailyTran.objects.filter(product__id__in=crop_ids,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 8)

