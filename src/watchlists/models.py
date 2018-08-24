from django.conf import settings
from django.db.models import (
    Model,
    CASCADE,
    CharField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    FloatField,
    QuerySet,
    TextField,
    SET_NULL,
    Q,
)
from django.utils.translation import ugettext_lazy as _
from configs.models import Config, AbstractProduct


COMPARISON_CHOICES = [
    ('__lt__', _('<')),
    ('__lte__', _('<=')),
    ('__gt__', _('>')),
    ('__gte__', _('>=')),
]

COLOR_CHOICES = [
    ('default', 'Default'),
    ('info', 'Info'),
    ('success', 'Success'),
    ('alert', 'Alert'),
    ('danger', 'Danger'),
]


class Watchlist(Model):
    name = CharField(max_length=120, unique=True, verbose_name=_('Name'))
    user = ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    is_default = BooleanField(default=False, verbose_name=_('Is Default'))
    watch_all = BooleanField(default=False, verbose_name=_('Watch All'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Updated'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Watchlist')
        verbose_name_plural = _('Watchlists')

    def save(self, *args, **kwargs):
        # set false if default watchlist exist
        if self.is_default:
            try:
                watchlist = Watchlist.objects.get(is_default=True)
                if self != watchlist:
                    watchlist.update(is_default=False)
            except Watchlist.DoesNotExist:
                pass

        # remove if watch all watchlist exist
        if self.watch_all:
            try:
                watchlist = Watchlist.objects.get(watch_all=True)
                if self != watchlist:
                    watchlist.delete()
            except Watchlist.DoesNotExist:
                pass

        super(Watchlist, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

    def children(self):
        return WatchlistItem.objects.filter(parent=self)

    def related_configs(self):
        return Config.objects.filter(id__in=self.children().values_list('product__config__id', flat=True).distinct()).order_by('id')

    @property
    def related_product_ids(self):
        ids = []
        for child in self.children():
            ids = ids + list(child.product.related_product_ids)
        return ids


class WatchlistItemQuerySet(QuerySet):
    """ for case like WatchlistItem.objects.filter(parent=self).filter_by_product(product__id=1) """
    def filter_by_product(self, **kwargs):
        product = kwargs.get('product') or AbstractProduct.objects.filter(id=kwargs.get('product__id')).first()

        if product:
            return self.filter(
                Q(product=product) |
                Q(product__parent=product) |
                Q(product__parent__parent=product) |
                Q(product__parent__parent__parent=product) |
                Q(product__parent__parent__parent__parent=product)
            )

        return self.none()
    """ 
    for case like QuerySet.get_unit()
    if QuerySet products has multiple types, search for parent unit by config.type_level
    if single type, return first product unit
    limit: same type of products(in single product chain) only support same unit 
    """
    def get_unit(self):
        config = self.first().product.config
        if self.values('product__type').count() > 0:
            if config.type_level == 1:
                unit = config.first_level_products().first().unit
            elif config.type_level == 2:
                unit = config.first_level_products().first().children().first().unit
            else:
                raise NotImplementedError('Can not locate product to access Unit object')
            return unit
        else:
            return self.first().unit


class WatchlistItem(Model):
    product = ForeignKey('configs.AbstractProduct', on_delete=CASCADE, verbose_name=_('Product'))
    sources = ManyToManyField('configs.Source', verbose_name=_('Source'))
    parent = ForeignKey('watchlists.Watchlist', null=True, on_delete=CASCADE, verbose_name=_('Parent'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    objects = WatchlistItemQuerySet.as_manager()

    class Meta:
        verbose_name = _('Watchlist Item')
        verbose_name_plural = _('Watchlist Items')

    def __str__(self):
        return str(self.product.name)

    def __unicode__(self):
        return str(self.product.name)


class MonitorProfile(Model):
    product = ForeignKey('configs.AbstractProduct', null=True, blank=True, on_delete=CASCADE, verbose_name=_('Product'))
    watchlist = ForeignKey('watchlists.Watchlist', null=True, blank=True, on_delete=CASCADE, verbose_name=_('Watchlist'))
    type = ForeignKey('configs.Type', null=True, blank=True, on_delete=SET_NULL, verbose_name=_('Type'))
    price = FloatField(verbose_name=_('Price'))
    comparison = CharField(max_length=6, default='__lt__', choices=COMPARISON_CHOICES, verbose_name=_('Comparison'))
    color = CharField(max_length=20, default='danger', choices=COLOR_CHOICES, verbose_name=_('Color'))
    info = TextField(null=True, blank=True, verbose_name=_('Info'))
    action = TextField(null=True, blank=True, verbose_name=_('Action'))
    period = TextField(null=True, blank=True, verbose_name=_('Period'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Monitor Profile')
        verbose_name_plural = _('Monitor Profile')

    def __str__(self):
        return str(self.product.name)

    def __unicode__(self):
        return str(self.product.name)

    def watchlist_items(self):
        return WatchlistItem.filter(product__parent=self.product)

    @property
    def format_price(self):
        d = dict(COMPARISON_CHOICES)
        comparison = d[str(self.comparison)]
        return '{0}{1:g}{2}'.format(comparison, self.price, self.product.unit.price_unit)













