from django import template

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
