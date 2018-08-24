from django import template
register = template.Library()


@register.filter
def index_filter(lst, i):
    return lst[int(i)]
