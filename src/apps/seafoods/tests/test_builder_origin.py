import datetime
import pytest
from django.core.management import call_command
from dashboard.testing import BuilderTestCase
from apps.seafoods.builder import direct_origin
from apps.dailytrans.models import DailyTran
from apps.seafoods.models import Seafood


@pytest.mark.secret
class BuilderTestCase(BuilderTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog13-test.yaml', verbosity=0)

        cls.start_date = datetime.date(year=2017, month=1, day=3)
        cls.end_date = datetime.date(year=2017, month=1, day=3)

    def test_direct_single(self):
        result = direct_origin(start_date=self.start_date, end_date=self.end_date)
        self.assertTrue(result.success)
        obj = Seafood.objects.filter(code='1011', type__id=2).first()
        self.assertIsNotNone(obj)
        children = obj.children()
        qs = DailyTran.objects.filter(product__id__in=children.values_list('id', flat=True),
                                      date__range=(self.start_date, self.end_date))
        self.assertEqual(qs.count(), 1)

    def test_direct_multi(self):
        start_date = datetime.date(year=2017, month=1, day=1)
        end_date = datetime.date(year=2017, month=1, day=10)
        direct_origin(start_date='2017/01/01', end_date='2017/01/10', format='%Y/%m/%d')
        obj = Seafood.objects.filter(code='1011', type__id=2).first()
        obj2 = Seafood.objects.filter(code='1011D', type__id=2).first()
        obj_ids = list(obj.children().values_list('id', flat=True)) + list(obj2.children().values_list('id', flat=True))
        qs = DailyTran.objects.filter(product__id__in=obj_ids,
                                      date__range=(start_date, end_date))
        self.assertEqual(qs.count(), 20)

    def test_duplicate_data(self):
        start_date = datetime.date(year=2015, month=7, day=28)
        end_date = datetime.date(year=2015, month=7, day=28)
        direct_origin(start_date=start_date, end_date=end_date)
        obj = Seafood.objects.filter(code='1171', type__id=2).first()  # 石斑
        qs = DailyTran.objects.filter(product__id__in=obj.children().values_list('id', flat=True),
                                      date__range=(start_date, end_date))
        self.assertEqual(qs.count(), 2)
