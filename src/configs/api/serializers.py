from rest_framework.serializers import (
    ModelSerializer,
)
from configs.models import (
    Config,
    AbstractProduct,
    Chart,
    Type,
    Source,
    Unit,
)


class ChartSerializer(ModelSerializer):
    class Meta:
        model = Chart
        fields = ['name', 'code']


class TypeSerializer(ModelSerializer):
    class Meta:
        model = Type
        fields = ['name']


class SourceSerializer(ModelSerializer):
    class Meta:
        model = Source
        fields = ['name']


class ConfigSerializer(ModelSerializer):
    class Meta:
        model = Config
        fields = ['name', 'code']


class AbstractProductSerializer(ModelSerializer):
    class Meta:
        model = AbstractProduct
        fields = ['name', 'code']


class UnitSerializer(ModelSerializer):
    class Meta:
        model = Unit
        fields = ['price_unit', 'volume_unit', 'weight_unit']



