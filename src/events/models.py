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
    BooleanField,
    Q,
)
from django.utils.translation import ugettext_lazy as _
from tagulous.models import (
    TagField,
    TagTreeModel,
)

EVENT_CONTENT_TYPE_CHOICES = (
    Q(app_label='configs', model='abstractproduct') |
    Q(app_label='configs', model='config')
)

DEFAULT_EVENT_CONTENT_TYPE_ID = ContentType.objects.get(model='abstractproduct').id


class EventType(TagTreeModel):
    class TagMeta:
        space_delimiter = False
        autocomplete_view = 'events:api:event_type_autocomplete'

    class Meta:
        verbose_name = _('Event Type')
        verbose_name_plural = _('Event Types')
        ordering = ('level',)

    def __str__(self):
        return str(self.label)

    def __unicode__(self):
        return str(self.label)


class Event(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, default=1)
    content_type = ForeignKey(ContentType,
                              default=DEFAULT_EVENT_CONTENT_TYPE_ID,
                              limit_choices_to=EVENT_CONTENT_TYPE_CHOICES,
                              on_delete=CASCADE)
    object_id = PositiveIntegerField(default=1)
    types = TagField(EventType, verbose_name=_('Event Type'), help_text=_('You can create new event type here'))
    name = CharField(max_length=120, unique=True, verbose_name=_('Name'))
    context = TextField(verbose_name=_('Context'))
    date = DateField(auto_now=False, default=timezone.now().today, verbose_name=_('Date'))
    share = BooleanField(default=False, verbose_name=_('Shared Event'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)





