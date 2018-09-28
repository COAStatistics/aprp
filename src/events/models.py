from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    ForeignKey,
    CASCADE,
    TextField,
    DateField,
    PositiveIntegerField,
    Q,
)
from django.utils.translation import ugettext_lazy as _


EVENT_CONTENT_TYPE_CHOICES = (
    Q(app_label='configs', model='abstractproduct') |
    Q(app_label='configs', model='config')
)
try:
    DEFAULT_EVENT_CONTENT_TYPE_ID = ContentType.objects.get(model='abstractproduct').id
except ContentType.DoesNotExist:
    DEFAULT_EVENT_CONTENT_TYPE_ID = 1


class EventType(Model):
    name = CharField(max_length=120, unique=True, verbose_name=_('Name'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Event Type')
        verbose_name_plural = _('Event Types')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)


class Event(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, default=1)
    content_type = ForeignKey(ContentType,
                              default=DEFAULT_EVENT_CONTENT_TYPE_ID,
                              limit_choices_to=EVENT_CONTENT_TYPE_CHOICES,
                              on_delete=CASCADE)
    object_id = PositiveIntegerField(default=1)
    type = ForeignKey('events.EventType', on_delete=CASCADE, verbose_name=_('Event Type'))
    name = CharField(max_length=120, unique=True, verbose_name=_('Name'))
    context = TextField(null=True, blank=True, verbose_name=_('Context'))
    date = DateField(auto_now=False, default=timezone.now().today, verbose_name=_('Date'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)





