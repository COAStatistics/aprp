from django import template
register = template.Library()


@register.filter
def round_filter(number, n=None):
    if isinstance(number, float) or isinstance(number, int):
        if isinstance(n, int):
            return round(number, n)
        else:
            return round(number)
    else:
        return ''
