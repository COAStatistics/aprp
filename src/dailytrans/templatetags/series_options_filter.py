from django import template
register = template.Library()


@register.filter
def index_length(series_options):
    indexes = {
        'avg_price': False,
        'sum_volume': False,
        'avg_weight': False,
    }
    for option in series_options:
        if option['no_data'] is False:
            for index in indexes.keys():
                if index in option['highchart']:
                    indexes[index] = True
    return int(indexes['avg_price']) + int(indexes['sum_volume']) + int(indexes['avg_weight'])





