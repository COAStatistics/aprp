from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string

from . import models
from . import forms


def post_socialwall(request):
    return HttpResponse('Hi')
