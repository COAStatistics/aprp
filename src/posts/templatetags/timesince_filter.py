from django import template
from django.utils import timezone
import datetime
import math

register = template.Library()


@register.filter
def timesince_filter(date, default="剛剛"):
    now = datetime.datetime.now(timezone.utc)
    diff = now - date
    periods = (
        (diff.days / 365, "年"),
        (diff.days / 30, "月"),
        (diff.days / 7, "星期"),
        (diff.days, "天"),
        (diff.seconds / 3600, "小時"),
        (diff.seconds / 60, "分鐘"),
        (diff.seconds, "秒"),
    )
    for period, singular in periods:
        if math.floor(period) > 0:
            return "%d%s" % (period, singular)
    return default