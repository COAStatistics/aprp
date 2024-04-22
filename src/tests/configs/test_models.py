import pytest

from apps.configs.models import (
    Config,
    Source, Type,
)
from tests.factories import (
    SourceFactory,
)


@pytest.mark.django_db
class TestUnitModel:
    def test_unit_instance(self, unit):
        assert unit.price_unit == "元/公斤"
        assert unit.volume_unit == "頭"
        assert unit.weight_unit == "公斤"
        assert unit.update_time is not None

    def test_unit_with_null_value(self, unit_with_null):
        assert unit_with_null.volume_unit is None
        assert unit_with_null.weight_unit is None

    def test_unit_str_method(self, unit):
        result = f"{unit.price_unit}, {unit.volume_unit}, {unit.weight_unit}"

        assert str(unit) == result

    def test_unit_attr_list_method(self, unit):
        # Arrange
        expected_result = [
            ("Price Unit", unit.price_unit),
            ("Volume Unit", unit.volume_unit),
            ("Weight Unit", unit.weight_unit),
        ]

        # Act
        result = unit.attr_list()

        # Assert
        assert result == expected_result


@pytest.mark.django_db
class TestTypeModel:
    def test_type_str(self, type_instance):
        # Act
        result = str(type_instance)

        # Assert
        assert result == type_instance.name

    def test_type_to_direct(self, type_instance):
        # Act
        result = type_instance.to_direct

        # Assert
        assert result is True


@pytest.mark.django_db
class TestSourceModel:
    def test_source(self, source):
        assert source.name is not None
        assert source.configs is not None
        assert source.type is not None
        assert source.enable is True
        assert source.update_time is not None

    def test_source_with_null_values(self, source_with_null_values):
        assert source_with_null_values.alias is None
        assert source_with_null_values.code is None
        assert source_with_null_values.type is None

    def test_source_configs(self, source_with_configs):
        configs = list(source_with_configs.configs.all())

        assert source_with_configs.configs.count() == len(configs)

        # Remove the config from the source
        config = configs.pop()
        source_with_configs.configs.remove(config)
        assert source_with_configs.configs.count() == len(configs)

        # Check reverse relationship
        filtered_configs = Config.objects.filter(source__name=source_with_configs.name)
        assert filtered_configs.count() == len(configs)

        # Check filter condition
        config = configs.pop()
        filtered_configs = Config.objects.filter(source__name=source_with_configs.name, name=config.name)
        assert filtered_configs.count() == len(configs)

        # Check reverse query
        source_instance = Source.objects.get(name=source_with_configs.name)
        configs = source_instance.configs.all()
        assert configs.count() == len(configs)

        # Check get source instance by config name
        source_instance = Source.objects.filter(configs__name=config.name)
        assert source_instance.count() == 1

    def test_source_type(self, source_with_type):
        type_instance = Type.objects.get(name=source_with_type.type.name)
        source = Source.objects.select_related('type').get(name=source_with_type.name)

        assert source.type is not None
        assert source.type.name == type_instance.name

    def test_simple_name_property(self):
        # Arrange
        source = SourceFactory.create(name='臺北一')

        # Act
        result = source.simple_name

        # Assert
        assert result == '台北一'

    # Happy path test for configs_flat property
    def test_configs_flat_property(self, source_with_configs):
        # Arrange
        expected_flat = ','.join([i.name for i in list(source_with_configs.configs.all())])

        # Act
        result = source_with_configs.configs_flat

        # Assert
        assert result == expected_flat

    def test_to_direct_property(self, source):
        # Act
        result = source.to_direct

        # Assert
        assert result is True
