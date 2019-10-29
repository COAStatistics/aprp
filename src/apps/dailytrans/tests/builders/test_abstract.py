from dashboard.testing import BuilderBackendTestCase
from apps.dailytrans.builders.eir030 import Api
from django.core.management import call_command
from apps.crops.models import Crop
from apps.fruits.models import Fruit


class AbstractBuilderTestCase(BuilderBackendTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # load fixtures
        call_command('loaddata', 'configs.yaml', verbosity=0)
        call_command('loaddata', 'sources.yaml', verbosity=0)
        call_command('loaddata', 'cog05-test.yaml', verbosity=0)
        call_command('loaddata', 'cog06-test.yaml', verbosity=0)

    def test_singular(self):
        api_crop = Api(model=Crop, config_code='COG05', type_id=1, logger_type_code='LOT-crops')
        api_fruit = Api(model=Fruit, config_code='COG06', type_id=1, logger_type_code='LOT-fruits')
        self.assertEqual(api_crop.MODEL, Crop)
        self.assertEqual(api_fruit.MODEL, Fruit)
        self.assertEqual(api_crop.LOGGER, api_fruit.LOGGER)
        self.assertNotEqual(api_crop.LOGGER_EXTRA, api_fruit.LOGGER_EXTRA)
        self.assertIsNotNone(api_fruit.PRODUCT_QS)
        self.assertIsNotNone(api_fruit.SOURCE_QS)
