import datetime
from django.core.management import call_command
from django.test import TestCase
from apps.seafoods.builder import direct


class BuilderTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog13-test.yaml', verbosity=0)

        self.start_date = datetime.date(year=2017, month=1, day=1)
        self.end_date = datetime.date(year=2017, month=1, day=3)

    def test_direct_delta(self):
        result = direct(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result.success)
