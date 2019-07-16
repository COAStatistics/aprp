import datetime
from django.core.management import call_command
from django.test import TestCase
from apps.rices.builder import direct
from apps.dailytrans.models import DailyTran
from apps.rices.models import Rice


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog01.yaml', verbosity=0)

        self.start_date = datetime.date(year=2019, month=1, day=2)
        self.end_date = datetime.date(year=2019, month=1, day=3)

    def test_direct_single(self):
        direct(start_date=self.start_date, end_date=self.end_date)
        obj = Rice.objects.filter(code='pt_1japt').first()

        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEquals(qs.count(), 2)

    def test_direct_multi(self):
        start_date = datetime.date(year=2019, month=1, day=1)
        end_date = datetime.date(year=2019, month=4, day=1)
        direct(start_date=start_date, end_date=end_date)

        qs = DailyTran.objects.filter(date__range=[start_date, end_date])

        self.assertEquals(qs.count(), 1365)

    def test_direct_delta(self):
        direct(delta=-3)

        end_date = datetime.date.today()
        start_date = end_date + datetime.timedelta(-3)

        count_1 = DailyTran.objects.filter(date__range=(start_date, end_date)).count()

        direct(start_date=start_date, end_date=end_date)

        count_2 = DailyTran.objects.filter(date__range=(start_date, end_date)).count()

        self.assertEquals(count_1, count_2)

        direct(start_date=start_date, end_date=end_date)
