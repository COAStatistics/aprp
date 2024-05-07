from factory import Faker, SubFactory

from apps.dailytrans.models import (
    DailyTran,
    DailyReport,
)
from tests.configs.factories import (
    SourceFactory,
    AbstractProductFactory,
)
from tests.factories import BaseFactory


class DailyTranFactory(BaseFactory):
    class Meta:
        model = DailyTran

    product = SubFactory(AbstractProductFactory)
    source = SubFactory(SourceFactory)
    up_price = Faker('pyfloat')
    mid_price = Faker('pyfloat')
    low_price = Faker('pyfloat')
    avg_price = Faker('pyfloat')
    avg_weight = Faker('pyfloat')


class DailyReportFactory(BaseFactory):
    class Meta:
        model = DailyReport

    date = Faker('date')
    file_id = Faker('uuid4')
