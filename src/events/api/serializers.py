from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    DateField,
)
from events.models import (
    EventType,
    Event,
)
from django.db.models import Q


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'


class EventSerializer(ModelSerializer):
    user = SerializerMethodField()
    types = EventTypeSerializer(many=True)
    date = DateField(format="%Y/%m/%d")

    def get_user(self, instance):
        return instance.user.info.full_name

    class Meta:
        model = Event
        fields = ['id', 'content_type', 'object_id', 'name', 'context', 'types', 'date', 'share', 'user']

    def parse_event_input(self):
        s = self.initial_data['types']
        if s:
            names = [name.strip() for name in s.split(',')]
            ids = []
            for name in names:
                obj = EventType.objects.filter(Q(label=name) | Q(name=name)).first()
                if not obj:
                    obj = EventType.objects.create(name='其他/'+name)
                ids.append(obj.id)
            return EventType.objects.filter(id__in=ids)
        return EventType.objects.none

    def update(self, instance, validated_data):
        instance = self.instance

        event_types = self.parse_event_input()

        # delete
        instance.types.all().exclude(id__in=event_types.values_list('id', flat=True)).delete()

        # create
        for obj in event_types:
            if obj not in instance.types.all():
                instance.types.add(obj)

        instance.save()

        return instance

    def create(self, validated_data):
        instance = Event.objects.create(**validated_data)
        event_types = self.parse_event_input()
        # create
        for obj in event_types:
            if obj not in instance.types.all():
                instance.types.add(obj)
        instance.save()
        return instance


