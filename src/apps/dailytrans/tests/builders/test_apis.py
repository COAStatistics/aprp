import datetime
from django.test import TestCase
from django.core.management import call_command
from apps.dailytrans.models import DailyTran
from apps.fruits.models import Fruit
from apps.dailytrans.builders.apis import Api


class BuilderTestCase(TestCase):

    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog06.yaml', verbosity=0)

        self.date = datetime.date(year=2017, month=1, day=1)

    def test_fruit(self):
        # test create
        obj = Fruit.objects.filter(name='青香蕉(內銷)').filter(track_item=True).first()

        api = Api(model=Fruit, config_code='COG06', type_id=2)
        response = api.request(start_date=self.date,
                               end_date=self.date,
                               name=obj.name)
        api.load(response)
        count_qs = DailyTran.objects.filter(date=self.date,
                                            product=obj)
        self.assertEquals(count_qs.count(), 5)

        # test update by load again

        api.load(response)

        self.assertEquals(count_qs.count(), 5)
