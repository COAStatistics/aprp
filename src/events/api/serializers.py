
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    DateField,
)
from events.models import (
    EventType,
    Event,
)


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'


class EventSerializer(ModelSerializer):
    type_name = SerializerMethodField()
    date = DateField(format="%Y/%m/%d")

    def get_type_name(self, instance):
        return instance.type.name

    class Meta:
        model = Event
        fields = ['id', 'content_type', 'object_id', 'name', 'context', 'type_name', 'type', 'date']
