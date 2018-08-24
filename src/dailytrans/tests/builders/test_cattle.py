import datetime
from django.test import TestCase
from django.core.management import call_command
from dailytrans.models import DailyTran
from cattles.models import Cattle
from dailytrans.builders.cattle import Api


class BuilderTestCase(TestCase):

    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'cog14.yaml', verbosity=0)

        self.date = datetime.date(year=2018, month=7, day=23)

    def test_cattle(self):
        # test create
        obj = Cattle.objects.filter(name='肥育乳公牛550公斤以上').filter(track_item=True).first()

        api = Api(model=Cattle, config_code='COG14', type_id=2)

        self.assertEquals(api.PRODUCT_QS.count(), 5)

        response = api.request(date=self.date)
        api.load(response)

        count_qs = DailyTran.objects.filter(date=self.date,
                                            product=obj)

        self.assertEquals(count_qs.count(), 1)

        # test update by load again
        api.load(response)

        self.assertEquals(count_qs.count(), 1)

    def test_multi(self):
        # test create
        api = Api(model=Cattle, config_code='COG14', type_id=2)

        response = api.request(date=self.date)
        api.load(response)

        count_qs = DailyTran.objects.filter(date=self.date, product__track_item=True)

        self.assertEquals(count_qs.count(), 5)





