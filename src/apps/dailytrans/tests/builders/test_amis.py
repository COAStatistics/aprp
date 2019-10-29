import datetime
import pytest
from dashboard.testing import BuilderBackendTestCase
from django.core.management import call_command
from apps.dailytrans.models import DailyTran
from apps.crops.models import Crop
from apps.flowers.models import Flower
from apps.configs.models import Source
from apps.dailytrans.builders.amis import Api


@pytest.mark.secret
class BuilderTestCase(BuilderBackendTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog02.yaml', verbosity=0)
        call_command('loaddata', 'cog07.yaml', verbosity=0)

        cls.date = datetime.date(year=2017, month=1, day=1)

    def test_crop(self):
        # test create
        obj = Crop.objects.filter(code='F').filter(track_item=True).first()
        source = Source.objects.filter_by_name('台北一').first()

        api = Api(model=Crop, config_code='COG02', type_id=1, market_type='V')
        response = api.request(date=self.date,
                               source=source.code)
        api.load(response)
        count_qs = DailyTran.objects.filter(date=self.date,
                                            product=obj)
        self.assertEqual(count_qs.count(), 1)

        # test update by load again

        api.load(response)

        self.assertEqual(count_qs.count(), 1)

    def test_flower(self):
        api = Api(model=Flower, config_code='COG07', type_id=1, market_type='V')
        self.assertEqual(api.PRODUCT_QS.count(), 50)
