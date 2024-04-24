import pytest

from apps.configs.models import (
    Config,
    Source,
    Type,
    Chart, FestivalName, Festival, AbstractProduct,
)
from tests.configs.factories import (
    SourceFactory,
    ChartFactory,
    MonthFactory,
    FestivalNameFactory,
)


@pytest.mark.django_db
class TestAbstractProductModel:
    def test_str_method(self, product_of_rice):
        assert str(product_of_rice) == product_of_rice.name

    def test_children_method(self, product_of_rice):
        # japt
        children = product_of_rice.children()

        assert children.count() == 1

        # pt_1japt and pt_2japt
        children = children.first().children()

        assert children.count() == 2
        assert children.first().children().count() == 0

    def test_children_all_method(self, product_of_rice):
        # japt, pt_1japt and pt_2japt
        children = product_of_rice.children_all()

        assert children.count() == 3

        # pt_1japt and pt_2japt
        children = children.first().children_all()

        assert children.count() == 2
        assert children.first().children_all().count() == 0

    def test_level_method(self, product_of_rice):
        parent = product_of_rice

        assert parent.level == 1

        rice_ja = parent.children().first()

        assert rice_ja.level == 2

    def test_to_direct_method(self, product_of_rice):
        parent = product_of_rice

        # Act
        result = parent.to_direct

        # Assert
        assert result is False

        # japt
        children = product_of_rice.children().first()

        # Act
        result = children.to_direct

        # Assert
        assert result is True

    def test_related_product_ids_method(self, product_of_rice):
        # Arrange
        result = sorted(product_of_rice.related_product_ids)

        # Act
        products = AbstractProduct.objects.filter(id__in=result)

        # Assert
        assert [product.id for product in products] == result


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

    def test_source_with_configs(self, source_with_configs):
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


@pytest.mark.django_db
class TestConfigModel:
    def test_config(self, config):
        assert config.name is not None
        assert config.code is not None
        assert config.charts is not None
        assert config.type_level in [1, 2]
        assert config.update_time is not None

    def test_config_with_charts(self, config_with_charts):
        charts = list(config_with_charts.charts.all())

        assert config_with_charts.charts.count() == len(charts)

        # Remove the chart from the config
        chart = charts.pop()
        config_with_charts.charts.remove(chart)
        assert config_with_charts.charts.count() == len(charts)

        # Check reverse relationship
        filtered_charts = Chart.objects.filter(config__name=config_with_charts.name)
        assert filtered_charts.count() == len(charts)

        # Check filter condition
        chart = charts.pop()
        filtered_charts = Chart.objects.filter(config__name=config_with_charts.name, name=chart.name)
        assert filtered_charts.count() == len(charts)

        # Check reverse query
        config = Config.objects.get(name=config_with_charts.name)
        charts = config.charts.all()
        assert charts.count() == len(charts)

        # Check get config instance by chart name
        configs = Config.objects.filter(charts__name=chart.name)
        assert configs.count() == 1

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


@pytest.mark.django_db
class TestChartModel:
    def test_chart_instance(self, chart):
        assert chart.name is not None
        assert chart.code is not None
        assert chart.template_name is not None
        assert chart.update_time is not None

    def test_chart_str_method(self, chart):
        # Act
        result = str(chart)

        # Assert
        assert result == chart.name

    def test_chart_unique_constraint(self, chart):
        # Act
        with pytest.raises(Exception):
            ChartFactory.create(name=chart.name)


@pytest.mark.django_db
class TestMonthModel:
    def test_month_instance(self, month):
        assert month.name is not None

    def test_month_str_method(self, month):
        # Act
        result = str(month)

        # Assert
        assert result == month.name

    def test_month_unique_constraint(self, month):
        # Act
        with pytest.raises(Exception):
            MonthFactory.create(name=month.name)


@pytest.mark.django_db
class TestFestivalNameModel:
    def test_festival_name_instance(self, festival_name):
        assert festival_name.name is not None
        assert festival_name.enable is True
        assert festival_name.lunar_month is not None
        assert festival_name.lunar_day is not None
        assert festival_name.create_time is not None
        assert festival_name.update_time is not None

    def test_festival_name_str_method(self, festival_name):
        # Act
        result = str(festival_name)

        # Assert
        assert result == festival_name.name

    def test_festival_name_unique_constraint(self, festival_name):
        # Act
        with pytest.raises(Exception):
            FestivalNameFactory.create(name=festival_name.name)


@pytest.mark.django_db
class TestFestivalModel:
    def test_festival_instance(self, festival):
        assert festival.roc_year is not None
        assert festival.name is not None
        assert festival.enable is True
        assert festival.create_time is not None
        assert festival.update_time is not None

        # testing relationship
        name = FestivalName.objects.get(name=festival.name.name)

        assert name is not None

        # testing reverse relationship
        festival_instance = name.festival_set.all().first()

        assert festival == festival_instance

        # testing delete cascade
        name.delete()

        with pytest.raises(Exception):
            FestivalName.objects.get(name=festival.name.id)

        festival_instance = Festival.objects.get(id=festival.id)
        assert festival_instance.name is None

    def test_festival_str(self, festival):
        assert str(festival) == f"{festival.roc_year}_{festival.name.name}"
