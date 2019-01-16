from django import template
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import datetime
import math
import pytz

register = template.Library()


@register.filter
def socialwall_posttime_filter(posttime):
    hour = posttime.hour + 8
    minute = posttime.minute
    if minute < 10:
        minute = '0{}'.format(str(minute))
    return "{}/{}/{} {}:{}".format(posttime.year, posttime.month, posttime.day, hour, minute)


@register.filter
def timediff_filter(updatetime):
    now = datetime.datetime.now(timezone.utc)
    diff = now - updatetime
    periods = (
        (diff.days / 365, _("years")),
        (diff.days / 30, _("months")),
        (diff.days / 7, _("weeks")),
        (diff.days, _("days")),
        (diff.seconds / 3600, _("hours")),
        (diff.seconds / 60, _("minutes")),
        (diff.seconds, _("seconds")),
    )
    for period, singular in periods:
        if math.floor(period) > 0:
            return "{} {} {}".format(math.floor(period), singular, _("ago"))
    if diff.seconds == 0:
        return "{}".format(_("now"))
    return "{} {} {}".format(diff.seconds, _("seconds"), _("ago"))


@register.filter
def editdiff_filter(updatetime):
    now = datetime.datetime.now(pytz.utc)
    now = datetime.datetime.strftime(now, "%Y-%m-%dT%H:%M:%S%Z")
    now = datetime.datetime.strptime(now, "%Y-%m-%dT%H:%M:%S%Z")
    updatetime = updatetime.split(".")[0] + "UTC"
    updatetime = datetime.datetime.strptime(updatetime, "%Y-%m-%dT%H:%M:%S%Z")
    diff = now - updatetime
    periods = (
        (diff.days / 365, _("years")),
        (diff.days / 30, _("months")),
        (diff.days / 7, _("weeks")),
        (diff.days, _("days")),
        (diff.seconds / 3600, _("hours")),
        (diff.seconds / 60, _("minutes")),
        (diff.seconds, _("seconds")),
    )
    for period, singular in periods:
        if math.floor(period) > 0:
            return "{} {} {}".format(math.floor(period), singular, _("ago"))
    if diff.seconds == 0:
        return "{}".format(_("now"))
    return "{} {} {}".format(diff.seconds, _("seconds"), _("ago"))
