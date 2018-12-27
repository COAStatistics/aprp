import datetime
from django.core.management import call_command
from django.test import TestCase
from rams.builder import direct
from dailytrans.models import DailyTran
from rams.models import Ram
from configs.models import Source
from django.db.models import Q


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog09.yaml', verbosity=0)

        self.start_date = datetime.date(year=2018, month=1, day=1)
        self.end_date = datetime.date(year=2018, month=1, day=2)

    def test_direct_single(self):
        direct(start_date=self.start_date, end_date=self.end_date)
        obj = Ram.objects.filter(code='G41').first()
        sources = Source.objects.filter(Q(name__exact='雲林縣') | Q(name__exact='彰化縣'))

        qs = DailyTran.objects.filter(product=obj,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 2)

    def test_direct_multi(self):
        direct(start_date='2018/01/01', end_date='2018/01/02', format='%Y/%m/%d')

        qs = DailyTran.objects.filter(date__range=(self.start_date, self.end_date))

        self.assertEquals(qs.count(), 2*2)

    def test_direct_delta(self):
        direct(delta=-3)

        end_date = datetime.date.today()
        start_date = end_date + datetime.timedelta(-3)

        count_1 = DailyTran.objects.filter(date__range=(start_date, end_date)).count()

        direct(start_date=start_date, end_date=end_date)

        count_2 = DailyTran.objects.filter(date__range=(start_date, end_date)).count()

        self.assertEquals(count_1, count_2)
