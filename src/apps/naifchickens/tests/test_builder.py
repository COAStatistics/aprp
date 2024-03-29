import datetime
from django.core.management import call_command
from dashboard.testing import BuilderTestCase
from apps.naifchickens.builder import direct
from apps.dailytrans.models import DailyTran
from apps.naifchickens.models import Naifchickens


class BuilderTestCase(BuilderTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'cog16.yaml', verbosity=0)

        cls.start_date = datetime.date(year=2018, month=7, day=16)
        cls.end_date = datetime.date(year=2018, month=7, day=23)

    def test_direct_single(self):
        result = direct(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result.success)
        obj = Naifchickens.objects.filter(code='環南-雞').first()
        qs = DailyTran.objects.filter(product=obj,
                                      date__range=(self.start_date, self.end_date))
        self.assertEqual(qs.count(), 2)

    def test_direct_multi(self):
        direct(start_date=self.start_date, end_date=self.end_date)

        qs = DailyTran.objects.filter(date__range=(self.start_date, self.end_date))

        self.assertEqual(qs.count(), 10)
