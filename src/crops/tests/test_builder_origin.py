import datetime
from django.core.management import call_command
from django.test import TestCase
from crops.builder import direct_origin
from dailytrans.models import DailyTran
from crops.models import Crop
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
        direct_origin(start_date=self.start_date, end_date=self.end_date)
        crop = Crop.objects.filter(code='落花生(帶殼)').first()

        qs = DailyTran.objects.filter(product=crop,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 8)

    def test_direct_multi(self):
        start_date = datetime.date(2017, 1, 1)
        end_date = datetime.date(2017, 1, 10)
        direct_origin(start_date=start_date, end_date=end_date)
        crop_ids = Crop.objects.filter(Q(code='落花生(帶殼)') | Q(code='紅豆(中等)')).values('id')

        qs = DailyTran.objects.filter(product__id__in=crop_ids,
                                      date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 42)
