from django.conf import settings


def ga_tracking_id(request):
    try:
        return {'ga_tracking_id': settings.GA_TRACKING_ID}
    except AttributeError:
        return {'ga_tracking_id': ''}


def use_ga(request):
    try:
        return {'use_ga': settings.USE_GA}
    except AttributeError:
        return {'use_ga', False}

