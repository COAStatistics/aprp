from django import template
from django.db.models.query import QuerySet
from apps.configs.models import (
    AbstractProduct,
    Config,
)
from apps.watchlists.models import MonitorProfile

register = template.Library()


@register.filter
def product_filter(product, watchlist):
    ids = []
    product_qs = product.children_all().filter(id__in=watchlist.related_product_ids).order_by('id')
    # seafood product exception: filter last level of products only
    for product in product_qs:
        if not product.children():
            ids.append(product.id)
    return product_qs.filter(id__in=ids) or AbstractProduct.objects.filter(id=product.id)


@register.filter
def source_filter(product, watchlist):
    return watchlist.children().filter_by_product(product=product).first().sources.order_by('id').values_list('name', flat=True)


@register.filter
def monitor_profile_filter(qs, watchlist):
    if isinstance(qs, QuerySet):
        return qs.filter(watchlist=watchlist)
    return None


@register.filter
def get_monitor_profile(obj, watchlist):
    if isinstance(obj, AbstractProduct):
        product_ids = list(obj.children_all().values_list('id', flat=True))
        product_ids.append(obj.id)
    elif isinstance(obj, Config):
        product_ids = obj.products().values_list('id', flat=True)
    else:
        return MonitorProfile.objects.none()

    monitor_profiles = MonitorProfile.objects.filter(product__id__in=product_ids, watchlist=watchlist, is_active=True)

    return monitor_profiles


@register.filter
def profile_color_filter(qs, color):
    return qs.filter(color=color)
