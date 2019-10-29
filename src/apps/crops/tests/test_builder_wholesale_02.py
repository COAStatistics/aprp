import datetime
import pytest
from django.core.management import call_command
from dashboard.testing import BuilderTestCase
from apps.crops.builder import direct_wholesale_02
from apps.dailytrans.models import DailyTran
from apps.crops.models import Crop
from apps.configs.models import Source
from django.db.models import Q


@pytest.mark.secret
class BuilderTestCase(BuilderTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog02.yaml', verbosity=0)

        cls.start_date = datetime.date(year=2017, month=1, day=1)
        cls.end_date = datetime.date(year=2017, month=1, day=3)

    def test_direct_single(self):
        direct_wholesale_02(start_date=self.start_date, end_date=self.end_date)
        crop = Crop.objects.filter(code='F').first()
        sources = Source.objects.filter(Q(name__exact='臺北一') | Q(name__exact='臺北二'))

        qs = DailyTran.objects.filter(product=crop,
                                      source__in=sources,
                                      date__range=(self.start_date, self.end_date))
        self.assertEqual(qs.count(), 4)

    def test_direct_multi(self):
        start_date = datetime.date(year=2017, month=1, day=1)
        end_date = datetime.date(year=2017, month=1, day=10)

        direct_wholesale_02(start_date=start_date, end_date=end_date)
        crop_ids = Crop.objects.filter(Q(code='F') | Q(code='O')).values('id')
        sources = Source.objects.filter(Q(name__exact='臺北一') | Q(name__exact='臺北二'))

        qs = DailyTran.objects.filter(product__id__in=crop_ids,
                                      source__in=sources,
                                      date__range=(start_date, end_date))
        self.assertEqual(qs.count(), 32)
