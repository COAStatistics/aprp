from factory import Faker

from apps.configs.models import (
    Last5YearsItems,
)
from tests.factories import *


class UnitFactory(BaseFactory):
    class Meta:
        model = "configs.Unit"

    price_unit = Faker('currency_name')
    volume_unit = Faker('word')
    weight_unit = Faker('word')


class TypeFactory(BaseFactory):
    class Meta:
        model = "configs.Type"

    name = Faker('name', 'zh_TW')


class SourceFactory(BaseFactory):
    class Meta:
        model = "configs.Source"

    name = Faker('name', 'zh_TW')
    alias = Faker('word', 'zh_TW')
    code = str(Faker('port_number'))
    type = factory.SubFactory("tests.configs.factories.TypeFactory")

    @factory.post_generation
    def configs(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for config in extracted:
                self.configs.add(config)
        else:
            self.configs.add(ConfigFactory())


class ConfigFactory(BaseFactory):
    class Meta:
        model = "configs.Config"

    name = Faker('name', 'zh_TW')
    code = Faker('license_plate')

    @factory.post_generation
    def charts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for chart in extracted:
                self.charts.add(chart)
        else:
            self.charts.add(ChartFactory())


class ChartFactory(BaseFactory):
    class Meta:
        model = "configs.Chart"

    name = Faker('name', 'zh_TW')
    code = Faker('word')
    template_name = Faker('uri_path')


class MonthFactory(BaseFactory):
    class Meta:
        model = "configs.Month"

    name = Faker('month_name', 'zh_TW')


class FestivalFactory(BaseFactory):
    class Meta:
        model = "configs.Festival"


class FestivalNameFactory(BaseFactory):
    class Meta:
        model = "configs.FestivalName"

    name = Faker('word', 'zh_TW')


class Last5YearsItemsFactory(BaseFactory):
    class Meta:
        model = Last5YearsItems

    year = Faker('year')
    item = Faker('word')

    config = factory.SubFactory(ConfigFactory)
    config_chart = factory.LazyAttribute(lambda o: f'{o.config.code}_{o.chart.code}')
    config_chart_year = factory.LazyAttribute(lambda o: f'{o.config.code}_{o.chart.code}_{o.year}')
