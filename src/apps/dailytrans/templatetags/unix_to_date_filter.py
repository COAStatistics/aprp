from django import template
from apps.dailytrans.utils import to_date
register = template.Library()


@register.filter
def unix_to_date_filter(string):
    date = to_date(string)
    return date.strftime('%Y-%m-%d')
