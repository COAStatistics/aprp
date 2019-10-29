import datetime
import pytest
from django.core.management import call_command
from dashboard.testing import BuilderTestCase
from apps.crops.builder import direct


@pytest.mark.secret
class BuilderTestCase(BuilderTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog02.yaml', verbosity=0)
        call_command('loaddata', 'cog05-test.yaml', verbosity=0)

        cls.start_date = datetime.date(year=2017, month=1, day=1)
        cls.end_date = datetime.date(year=2017, month=1, day=3)

    def test_direct_delta(self):
        result = direct(delta=-1)
        self.assertTrue(result.success)

        result2 = direct(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result2.success)
