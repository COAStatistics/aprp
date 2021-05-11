from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager
from django.db.models import (
    Model,
    QuerySet,
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    IntegerField,
    BooleanField,
    Q,
)
from django.utils import timezone

class AbstractProduct(Model):
    name = CharField(max_length=50, verbose_name=_('Name'))
    code = CharField(max_length=50, verbose_name=_('Code'))
    config = ForeignKey('configs.Config', null=True, on_delete=SET_NULL, verbose_name=_('Config'))
    type = ForeignKey('configs.Type', null=True, on_delete=SET_NULL, verbose_name=_('Type'))
    unit = ForeignKey('configs.Unit', null=True, blank=True, verbose_name=_('Unit'))
    parent = ForeignKey('self', null=True, blank=True, on_delete=SET_NULL, verbose_name=_('Parent'))
    track_item = BooleanField(default=True, verbose_name=_('Track Item'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    objects = InheritanceManager()

    class Meta:
        verbose_name = _('Abstract Product')
        verbose_name_plural = _('Abstract Products')
        ordering = ('id',)

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

    def children(self, watchlist=None):
        products = AbstractProduct.objects.filter(parent=self).select_subclasses()
        if watchlist:
            if not watchlist.watch_all:
                products = products.filter(id__in=watchlist.related_product_ids)
        return products.order_by('id')

    def children_all(self):
        return AbstractProduct.objects.filter(
            Q(parent=self)
            | Q(parent__parent=self)
            | Q(parent__parent__parent=self)
            | Q(parent__parent__parent__parent=self)
            | Q(parent__parent__parent__parent__parent=self)
        ).select_subclasses().order_by('id')

    def types(self, watchlist=None):
        if self.has_child:
            products = self.children()
            if watchlist:
                if not watchlist.watch_all:
                    products = products.filter(id__in=watchlist.related_product_ids)
            type_ids = products.values_list('type__id', flat=True)
            return Type.objects.filter(id__in=type_ids)
        elif self.type:
            return Type.objects.filter(id=self.type.id)
        else:
            return self.objects.none()

    def sources(self, watchlist=None):
        if watchlist:
            return watchlist.children().filter(product__id=self.id).first().sources.all()
        else:
            return Source.objects.filter(configs__id__exact=self.config.id).filter(type=self.type).order_by('id')

    @property
    def to_direct(self):
        """
        set true to navigate at front end
        """
        type_level = self.config.type_level
        return self.level >= type_level

    @property
    def has_source(self):
        return self.sources().count() > 0

    @property
    def has_child(self):
        return self.children().count() > 0

    @property
    def level(self):
        level = 1

        lock = False
        product = self

        while not lock:

            if product.parent is not None:
                product = product.parent
                level = level + 1
            else:
                lock = True

        return level

    @property
    def related_product_ids(self):
        ids = list(self.children().values_list('id', flat=True))

        lock = False
        product = self

        while not lock:
            ids.append(product.id)
            if product.parent is not None:
                product = product.parent
            else:
                lock = True

        return ids


class Config(Model):
    name = CharField(max_length=50, unique=True, verbose_name=_('Name'))
    code = CharField(max_length=50, unique=True, null=True, verbose_name=_('Code'))
    charts = ManyToManyField('configs.Chart', blank=True, verbose_name=_('Chart'))
    type_level = IntegerField(choices=[(1, 1), (2, 2)], default=1, verbose_name=_('Type Level'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Config')
        verbose_name_plural = _('Configs')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

    def products(self):
        # Use select_subclasses() to return subclass instance
        return AbstractProduct.objects.filter(config=self).select_subclasses().order_by('id')

    def first_level_products(self, watchlist=None):
        # Use select_subclasses() to return subclass instance
        products = AbstractProduct.objects.filter(config=self).filter(parent=None).select_subclasses()
        if watchlist:
            if not watchlist.watch_all:
                products = products.filter(id__in=watchlist.related_product_ids)
        return products.order_by('id')

    def types(self):
        products_qs = self.products().values('type').distinct()
        types_ids = [p['type'] for p in products_qs]
        types_qs = Type.objects.filter(id__in=types_ids)
        return types_qs

    @property
    def to_direct(self):
        """
        set true to navigate at front end
        """
        return False


class SourceQuerySet(QuerySet):
    """ for case like Source.objects.filter(config=config).filter_by_name(name) """
    def filter_by_name(self, name):
        if not isinstance(name, str):
            raise TypeError
        name = name.replace('台', '臺')
        qs = self.filter(name=name)
        if not qs:
            qs = self.filter(alias__icontains=name)
        return qs


class Source(Model):
    name = CharField(max_length=50, verbose_name=_('Name'))
    alias = CharField(max_length=255, null=True, blank=True, verbose_name=_('Alias'))
    code = CharField(max_length=50, null=True, blank=True, verbose_name=_('Code'))
    configs = ManyToManyField('configs.Config', verbose_name=_('Config'))
    type = ForeignKey('configs.Type', null=True, blank=True, on_delete=SET_NULL, verbose_name=_('Type'))
    enable = BooleanField(default=True, verbose_name=_('Enabled'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    objects = SourceQuerySet.as_manager()

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')
        ordering = ('id',)

    def __str__(self):
        flat = self.configs_flat
        return str(self.name) + '(%s-%s)' % (flat, self.type.name)

    def __unicode__(self):
        flat = self.configs_flat
        return str(self.name) + '(%s-%s)' % (flat, self.type.name)

    @property
    def simple_name(self):
        return self.name.replace('臺', '台')

    @property
    def configs_flat(self):
        return ','.join(config.name for config in self.configs.all())

    @property
    def to_direct(self):
        """
        set true to navigate at front end
        """
        return True


class TypeQuerySet(QuerySet):
    def filter_by_watchlist_items(self, **kwargs):
        items = kwargs.get('watchlist_items')
        if not items:
            raise NotImplementedError
        return self.filter(id__in=items.values_list('product__type__id', flat=True))


class Type(Model):
    name = CharField(max_length=50, unique=True, verbose_name=_('Name'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    objects = TypeQuerySet.as_manager()

    class Meta:
        verbose_name = _('Type')
        verbose_name_plural = _('Types')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

    def sources(self):
        return Source.objects.filter(type=self)

    @property
    def to_direct(self):
        """
        set true to navigate at front end
        """
        return True


class Unit(Model):
    price_unit = CharField(max_length=50, null=True, blank=True, verbose_name=_('Price Unit'))
    volume_unit = CharField(max_length=50, null=True, blank=True, verbose_name=_('Volume Unit'))
    weight_unit = CharField(max_length=50, null=True, blank=True, verbose_name=_('Weight Unit'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')

    def __str__(self):
        return '%s, %s, %s' % (self.price_unit, self.volume_unit, self.update_time)

    def __unicode__(self):
        return '%s, %s, %s' % (self.price_unit, self.volume_unit, self.update_time)

    def attr_list(self):
        lst = []
        for attr, value in self.__dict__.items():
            if attr in ['price_unit', 'volume_unit', 'weight_unit'] and value:
                lst.append((Unit._meta.get_field(attr).verbose_name.title(), value))
        return lst


class Chart(Model):
    name = CharField(max_length=120, unique=True, verbose_name=_('Name'))
    code = CharField(max_length=50, unique=True, null=True, verbose_name=_('Code'))
    template_name = CharField(max_length=255, verbose_name=_('Template Name'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))

    class Meta:
        verbose_name = _('Chart')
        verbose_name_plural = _('Charts')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)


class Month(Model):
    name = CharField(max_length=120, unique=True, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Month')
        verbose_name_plural = _('Months')

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return str(self.name)

        
class Festival(Model):
    roc_year = CharField(max_length=3, default=timezone.now().year-1911, verbose_name=_('ROC Year'))
    name = ForeignKey('configs.FestivalName', null=True, blank=True, on_delete=SET_NULL, verbose_name=_('Name'))
    enable = BooleanField(default=True, verbose_name=_('Enabled'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Created'))

    class Meta:
        verbose_name = _('Festival')
        verbose_name_plural = _('Festivals')
        ordering = ('id',)

    def __str__(self):
        return self.roc_year + '_' + self.name.name

    def __unicode__(self):
        return self.roc_year + '_' + self.name.name


class FestivalName(Model):
    name = CharField(max_length=20, verbose_name=_('Name'))
    enable = BooleanField(default=True, verbose_name=_('Enabled'))
    lunarmonth = CharField(max_length=2, default='01', verbose_name=_('LunarMonth'))
    lunarday = CharField(max_length=2, default='01', verbose_name=_('LunarDay'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Created'))

    class Meta:
        verbose_name = _('FestivalName')
        ordering = ('id',)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class FestivalItems(Model):
    name = CharField(max_length=20, verbose_name=_('Name'))
    enable = BooleanField(default=True, verbose_name=_('Enabled'))
    order_sn = IntegerField(default=9, verbose_name=_('Order SN'))
    festivalname = ManyToManyField('configs.FestivalName', verbose_name=_('FestivalName'))
    product_id = ManyToManyField('configs.AbstractProduct', verbose_name=_('Product_id'))
    source = ManyToManyField('configs.Source', verbose_name=_('Source'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Created'))

    class Meta:
        verbose_name = _('FestivalItem')
        ordering = ('order_sn',)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Last5YearsItems(Model):
    name = CharField(max_length=60, verbose_name=_('Name'))
    enable = BooleanField(default=True, verbose_name=_('Enabled'))
    product_id = ManyToManyField('configs.AbstractProduct', verbose_name=_('Product_id'))
    source = ManyToManyField('configs.Source', verbose_name=_('Source'))
    update_time = DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_('Updated'))
    create_time = DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('Created'))

    class Meta:
        verbose_name = _('Last5YearsItems')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name