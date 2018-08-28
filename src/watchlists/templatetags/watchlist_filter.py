from django import template
from configs.models import(
    AbstractProduct,
    Config,
)
from watchlists.models import MonitorProfile

register = template.Library()


@register.filter
def product_filter(product, watchlist):
    ids = []
    product_qs = product.children_all().filter(id__in=watchlist.related_product_ids).order_by('id')
    # seafood product exception: filter last level of products only
    for product in product_qs:
        if not product.children():
            ids.append(product.id)
    return product_qs.filter(id__in=ids)


@register.filter
def source_filter(product, watchlist):
    return watchlist.children().filter_by_product(product=product).first().sources.order_by('id').values_list('name', flat=True)


@register.filter
def monitor_profile_filter(obj, watchlist):
    if isinstance(obj, AbstractProduct):
        product_ids = list(obj.children_all().values_list('id', flat=True))
        product_ids.append(obj.id)
    elif isinstance(obj, Config):
        product_ids = obj.products().values_list('id', flat=True)
    else:
        raise NotImplementedError('Invalid obj parameter for this filter')

    monitor_profiles = MonitorProfile.objects.filter(product__id__in=product_ids, watchlist=watchlist, active=True)

    return monitor_profiles


@register.filter
def profile_color_filter(qs, color):
    return qs.filter(color=color)







