from django.utils import timezone
from django.db.models import (
    Model,
    CASCADE,
    DateTimeField,
    DateField,
    ForeignKey,
    FloatField,
    QuerySet,
    IntegerField,
    CharField,
)
from django.utils.translation import ugettext_lazy as _


class DailyTranQuerySet(QuerySet):
    def update(self, *args, **kwargs):
        kwargs['update_time'] = timezone.now()
        super(DailyTranQuerySet, self).update(*args, **kwargs)

    def between_month_day_filter(self, start_date=None, end_date=None):
        if start_date and end_date:
            start_md = int(start_date.strftime('%m%d'))
            end_md = int(end_date.strftime('%m%d'))

            ids = []
            for obj in self.all():
                if start_md <= obj.month_day <= end_md:
                    ids.append(obj.id)
            return self.filter(id__in=ids)

        elif start_date and end_date is None:
            return self.filter(date__month__gte=start_date.month, date__day__gte=start_date.day)
        elif end_date and start_date is None:
            return self.filter(date__month__lte=end_date.month, date__day__lte=end_date.day)
        else:
            return self


class DailyTran(Model):
    product = ForeignKey('configs.AbstractProduct', on_delete=CASCADE, verbose_name=_('Product'))
    source = ForeignKey('configs.Source', null=True, blank=True, on_delete=CASCADE, verbose_name=_('Source'))
    up_price = FloatField(null=True, blank=True, verbose_name=_('Up Price'))
    mid_price = FloatField(null=True, blank=True, verbose_name=_('Mid Price'))
    low_price = FloatField(null=True, blank=True, verbose_name=_('Low Pirce'))
    avg_price = FloatField(verbose_name=_('Average Price'))
    avg_weight = FloatField(null=True, blank=True, verbose_name=_('Average Weight'))
    volume = FloatField(null=True, blank=True, verbose_name=_('Volume'))
    date = DateField(auto_now=False, default=timezone.now().today, verbose_name=_('Date'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))
    not_updated = IntegerField(default=0, verbose_name=_('Not Updated Count'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Create Time'))

    objects = DailyTranQuerySet.as_manager()

    class Meta:
        verbose_name = _('Daily Transition')
        verbose_name_plural = _('Daily Transitions')

    def __str__(self):
        return 'product: %s, source: %s, avg_price: %s, volume: %s, avg_weight: %s, date: %s, updated: %s' % (
            self.product.name, self.source, self.avg_price, self.volume, self.avg_weight, self.date, self.update_time
        )

    def __unicode__(self):
        return 'product: %s, source: %s, avg_price: %s, volume: %s, avg_weight: %s, date: %s, updated: %s' % (
            self.product.name, self.source, self.avg_price, self.volume, self.avg_weight, self.date, self.update_time
        )

    @property
    def month_day(self):
        return int(self.date.strftime('%m%d'))


class DailyReport(Model):
    date = DateField(auto_now=False, default=timezone.now().today, verbose_name=_('Date'))
    file_id = CharField(max_length=120, unique=True, verbose_name=_('File ID'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Created'))

    class Meta:
        verbose_name = _('Daily Report')
        verbose_name_plural = _('Daily Reports')

    def __str__(self):
        return '{}, {}'.format(self.date, self.file_id)


class FestivalReport(Model):
    festival_id = ForeignKey('configs.Festival', on_delete=CASCADE, verbose_name=_('Festival ID'))
    file_id = CharField(max_length=120, unique=True, verbose_name=_('File ID'))
    file_volume_id = CharField(max_length=120, null=True, blank=True, verbose_name=_('File Volume ID'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Created'))

    class Meta:
        verbose_name = _('Festival Report')
        verbose_name_plural = _('Festival Reports')

    def __str__(self):
        return '{}, {}, {}'.format(self.festival_id, self.file_id, self.file_volume_id)
