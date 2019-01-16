import datetime
from django.test import TestCase
from django.core.management import call_command
from apps.dailytrans.models import DailyTran
from apps.rams.models import Ram
from apps.configs.models import Source
from apps.dailytrans.builders.eir107 import Api


class BuilderTestCase(TestCase):

    def setUp(self):
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog09.yaml', verbosity=0)

        self.date = datetime.date(year=2018, month=1, day=1)

    def test_ram(self):
        # test create
        obj = Ram.objects.filter(code='G41').filter(track_item=True).first()
        source = Source.objects.filter_by_name('彰化縣').first()

        api = Api(model=Ram, config_code='COG09', type_id=None)
        response = api.request(date=self.date,
                               source=source.name,
                               code=obj.code)

        api.load(response)
        count_qs = DailyTran.objects.filter(date=self.date,
                                            product=obj)
        self.assertEquals(count_qs.count(), 1)

        # test update by load again

        api.load(response)

        self.assertEquals(count_qs.count(), 1)
