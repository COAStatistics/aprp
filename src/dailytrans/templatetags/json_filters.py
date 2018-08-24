import json
from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet

register = template.Library()


@register.filter
def stringify(obj):

    def to_str(item):
        return item.__str__()

    if isinstance(obj, QuerySet):
        return serialize('json', obj)

    return json.dumps(obj, default=to_str)
