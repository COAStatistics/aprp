from django.core.management import call_command
from django.test import TestCase
import logging

from apps.logs.models import LogType, Log


class HandlerTestCase(TestCase):
    def setUp(self):
        # load fixtures
        call_command('loaddata', 'logs.yaml', verbosity=0)

        self.logger = logging.getLogger('aprp')

    def test_fixture(self):
        logger_types = LogType.objects.filter(code='LOT-crops')
        self.assertEquals(logger_types.count(), 1)

    def test_logger(self):
        try:
            '2' / 0
        except Exception as e:
            extra = {
                'type_code': 'LOT-crops',
            }
            self.logger.error(e, extra=extra)

        logs = Log.objects.filter(type__code='LOT-crops')
        self.assertEquals(logs.count(), 1)
