import datetime
from django.core.management import call_command
from django.test import TestCase
from flowers.builder import direct_wholesale_04
from dailytrans.models import DailyTran
from flowers.models import Flower
from configs.models import Source
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog04.yaml', verbosity=0)

        self.start_date = datetime.date(year=2018, month=3, day=6)
        self.end_date = datetime.date(year=2018, month=3, day=8)

    def test_direct_single(self):
        result = direct_wholesale_04(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result.success)

        obj = Flower.objects.filter(code='L', track_item=True).first()
        self.assertIsNotNone(obj)
        sources = Source.objects.filter(Q(name__exact='臺北花市') | Q(name__exact='臺中市場'))

        qs = DailyTran.objects.filter(product=obj,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 4)


