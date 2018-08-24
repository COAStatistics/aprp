import datetime
from django.test import TestCase
from django.core.management import call_command
from dailytrans.models import DailyTran
from crops.models import Crop
from configs.models import Source
from dailytrans.builders.eir030 import Api


class BuilderTestCase(TestCase):

    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog05.yaml', verbosity=0)

        self.start_date = datetime.date(year=2017, month=1, day=1)
        self.end_date = datetime.date(year=2017, month=1, day=1)

    def test_crop(self):
        # test create
        obj = Crop.objects.filter(code='LA1').filter(track_item=True).first()
        source = Source.objects.filter_by_name('台北一').first()

        api = Api(model=Crop, config_code='COG05', type_id=None)
        response = api.request(start_date=self.start_date,
                               end_date=self.end_date,
                               source=source.simple_name,
                               code=obj.code)
        api.load(response)
        count_qs = DailyTran.objects.filter(date=self.start_date,
                                            product=obj)
        self.assertEquals(count_qs.count(), 1)

        # test update by load again

        api.load(response)

        self.assertEquals(count_qs.count(), 1)


