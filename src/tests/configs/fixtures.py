import pytest

from tests.configs.factories import (
    UnitFactory,
    TypeFactory,
    ConfigFactory,
    SourceFactory,
    ChartFactory,
    MonthFactory,
    FestivalNameFactory,
    FestivalFactory,
)


@pytest.fixture
def unit():
    return UnitFactory(
        price_unit="元/公斤",
        volume_unit="頭",
        weight_unit="公斤",
    )


@pytest.fixture
def unit_with_null():
    return UnitFactory(
        price_unit="元/公斤",
        volume_unit=None,
        weight_unit=None,
    )


@pytest.fixture
def type_instance():
    return TypeFactory()


@pytest.fixture
def config(chart):
    return ConfigFactory(charts=[chart])


@pytest.fixture
def configs():
    return ConfigFactory.create_batch(3)


@pytest.fixture
def config_with_charts(charts):
    return ConfigFactory(charts=charts)


@pytest.fixture
def source(config, type_instance):
    return SourceFactory(configs=[config], type=type_instance)


@pytest.fixture
def source_with_null_values():
    return SourceFactory(
        name="台北一",
        alias=None,
        code=None,
        type=None,
    )


@pytest.fixture
def source_with_configs(configs):
    return SourceFactory(configs=configs)


@pytest.fixture
def source_with_type(type_instance):
    return SourceFactory(type=type_instance)


@pytest.fixture
def chart():
    return ChartFactory()


@pytest.fixture
def charts():
    return ChartFactory.create_batch(3)


@pytest.fixture
def month():
    return MonthFactory()


@pytest.fixture
def festival_name():
    return FestivalNameFactory()


@pytest.fixture
def festival_names():
    return FestivalNameFactory.create_batch(3)


@pytest.fixture
def festival(festival_name):
    return FestivalFactory(name=festival_name)
