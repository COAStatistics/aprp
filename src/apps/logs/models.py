from django.db.models import (
    Model,
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    DurationField,
)
from django.utils.translation import ugettext_lazy as _
from django_db_logger.models import StatusLog


class Log(StatusLog):
    type = ForeignKey('logs.LogType', null=True, on_delete=SET_NULL, verbose_name=_('Log Type'))
    url = CharField(max_length=255, null=True, blank=True, verbose_name=_('Url'))
    duration = DurationField(null=True, blank=True, verbose_name=_('Duration'))

    class Meta:
        verbose_name = _('Log')
        verbose_name_plural = _('Logs')


class LogType(Model):
    name = CharField(max_length=255, verbose_name=_('Name'))
    code = CharField(max_length=50, null=True, blank=True, verbose_name=_('Code'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('LogType')
        verbose_name_plural = _('LogTypes')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)
