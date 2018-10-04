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
from tagulous.utils import (
    clean_tree_name,
    split_tree_name
)
from rest_framework.exceptions import ValidationError


class EventTypeSerializer(ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'


class EventSerializer(ModelSerializer):
    user = SerializerMethodField()
    types = EventTypeSerializer(many=True)
    date = DateField(format="%Y/%m/%d")

    event_types_ids = []

    def get_user(self, instance):
        return instance.user.info.full_name

    def validate_types(self, data):
        self.event_types_ids = []
        is_valid = True
        names = [name.strip() for name in self.initial_data['types'].split(',')]
        names = list(set(names))
        names_to_create = []
        for name in names:
            clean_name = clean_tree_name(name)

            if clean_name != name:
                is_valid = False
            elif clean_name:
                obj = EventType.objects.filter(Q(label=clean_name) | Q(name=clean_name)).first()
                if obj:
                    self.event_types_ids.append(obj.id)
                    self.event_types_ids += list(obj.get_ancestors().values_list('id', flat=True))
                # create if not exist
                else:
                    count = len(split_tree_name(clean_name))
                    if count == 1:
                        clean_name = '其他/' + clean_name  # make '自訂' -> '其他/自訂'
                    names_to_create.append(clean_name)

        if not is_valid:
            raise ValidationError('Invalid token.')

        for name in names_to_create:
            obj = EventType.objects.create(name=name)
            self.event_types_ids.append(obj.id)
            self.event_types_ids += list(obj.get_ancestors().values_list('id', flat=True))

    class Meta:
        model = Event
        fields = ['id', 'content_type', 'object_id', 'name', 'context', 'types', 'date', 'share', 'user']

    def update(self, instance, validated_data):
        validated_data.pop('types', None)  # pop types key cause it is nested, not support in update()
        instance = super(EventSerializer, self).update(instance, validated_data)

        event_types = EventType.objects.filter(id__in=self.event_types_ids)

        # delete
        print(event_types)
        for obj in instance.types.exclude(id__in=self.event_types_ids).all():
            instance.types.remove(obj)
        # create
        for obj in event_types:
            if obj not in instance.types.all():
                instance.types.add(obj)

        instance.save()
        return instance

    def create(self, validated_data):
        instance = Event.objects.create(**validated_data)
        event_types = EventType.objects.filter(id__in=self.event_types_ids)
        # create
        for obj in event_types:
            if obj not in instance.types.all():
                instance.types.add(obj)
        instance.save()
        return instance


