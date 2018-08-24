import datetime
from django.test import TestCase
from django.core.management import call_command
from dailytrans.models import DailyTran
from crops.models import Crop
from flowers.models import Flower
from configs.models import Source
from dailytrans.builders.amis import Api


class BuilderTestCase(TestCase):

    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog02.yaml', verbosity=0)
        call_command('loaddata', 'cog07.yaml', verbosity=0)

        self.date = datetime.date(year=2017, month=1, day=1)

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
        self.assertEquals(count_qs.count(), 1)

        # test update by load again

        api.load(response)

        self.assertEquals(count_qs.count(), 1)

    def test_flower(self):
        api = Api(model=Flower, config_code='COG07', type_id=1, market_type='V')
        self.assertEquals(api.PRODUCT_QS.count(), 50)
