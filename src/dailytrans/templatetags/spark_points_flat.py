from django import template

register = template.Library()


@register.filter
def spark_points_flat(lst, key):
    """
    :param lst: list of dictionary
    :param key: key value want to flat
    :return: string flat with ','
    """
    return ','.join(str(dic[key]) for dic in lst)

