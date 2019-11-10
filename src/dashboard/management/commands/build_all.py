import logging
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

import apps.crops.builder
import apps.cattles.builder
import apps.rams.builder
import apps.flowers.builder
import apps.fruits.builder
import apps.chickens.builder
import apps.ducks.builder
import apps.gooses.builder
import apps.hogs.builder
import apps.rices.builder
import apps.seafoods.builder
import apps.hogs.builder


logger = logging.getLogger('factory')


class Command(BaseCommand):
    help = 'Build test data for all products at once.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, help='Days to build the test data.', default=14)

    def handle(self, **kwargs):
        days = kwargs.get('days')

        end = datetime.today()
        start = end - timedelta(days)

        apps.crops.builder.direct(start, end)
        apps.cattles.builder.direct(start, end)
        apps.rams.builder.direct(start, end)
        apps.flowers.builder.direct(start, end)
        apps.fruits.builder.direct(start, end)
        apps.chickens.builder.direct(start, end)
        apps.ducks.builder.direct(start, end)
        apps.gooses.builder.direct(start, end)
        apps.hogs.builder.direct(start, end)
        apps.rices.builder.direct(start, end)
        apps.seafoods.builder.direct(start, end)
        apps.hogs.builder.direct(start, end)
