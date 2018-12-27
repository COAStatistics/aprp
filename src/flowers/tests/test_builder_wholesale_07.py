import datetime
from django.core.management import call_command
from django.test import TestCase
from flowers.builder import direct_wholesale_07
from dailytrans.models import DailyTran
from flowers.models import Flower
from configs.models import Source
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog07.yaml', verbosity=0)

        self.start_date = datetime.date(year=2018, month=3, day=6)
        self.end_date = datetime.date(year=2018, month=3, day=6)

    def test_direct_single(self):
        direct_wholesale_07(start_date=self.start_date, end_date=self.end_date)
        obj = Flower.objects.filter(code='FB', track_item=True).first()
        sources = Source.objects.filter(Q(name__exact='臺北花市') | Q(name__exact='臺中市場'))

        qs = DailyTran.objects.filter(product=obj,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 2)

    def test_direct_multi(self):
        direct_wholesale_07(start_date='2018/02/07', end_date='2018/2/10', format='%Y/%m/%d')
        start_date = datetime.date(year=2018, month=2, day=7)
        end_date = datetime.date(year=2018, month=2, day=10)
        obj_ids = Flower.objects.filter(Q(code='FB') | Q(code='FO3')).values('id')
        sources = Source.objects.filter(Q(name__exact='臺北花市') | Q(name__exact='臺中市場'))

        qs = DailyTran.objects.filter(product__id__in=obj_ids,
                                      source__in=sources,
                                      date__range=(start_date, end_date))
        self.assertEquals(qs.count(), 8)
