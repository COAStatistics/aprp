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
        fields = '__all__'


class TypeSerializer(ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class SourceSerializer(ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class ConfigSerializer(ModelSerializer):
    class Meta:
        model = Config
        fields = '__all__'


class AbstractProductSerializer(ModelSerializer):
    class Meta:
        model = AbstractProduct
        fields = '__all__'


class UnitSerializer(ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'



