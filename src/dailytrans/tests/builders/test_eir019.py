import datetime
from django.test import TestCase
from django.core.management import call_command
from dailytrans.models import DailyTran
from hogs.models import Hog
from configs.models import Source
from dailytrans.builders.eir019 import Api


class BuilderTestCase(TestCase):

    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog08.yaml', verbosity=0)

        self.date = datetime.date(year=2018, month=1, day=3)

    def test_hog(self):
        # test create
        obj = Hog.objects.filter(code='規格豬(75公斤以上)').filter(track_item=True).first()
        source = Source.objects.filter_by_name('台中大安').first()

        api = Api(model=Hog, config_code='COG08', type_id=None)

        response = api.request(date=self.date,
                               source=source.simple_name)
        api.load(response)

        count_qs = DailyTran.objects.filter(date=self.date,
                                            product=obj)

        self.assertEquals(count_qs.count(), 1)

        # test update by load again
        api.load(response)

        self.assertEquals(count_qs.count(), 1)

    def test_multi(self):
        # test create
        obj = Hog.objects.filter(code='規格豬(75公斤以上)').filter(track_item=True).first()

        api = Api(model=Hog, config_code='COG08', type_id=None)

        response = api.request(date=self.date)
        api.load(response)

        count_qs = DailyTran.objects.filter(date=self.date, product=obj)

        self.assertEquals(count_qs.count(), 22)
