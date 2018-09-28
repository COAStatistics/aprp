from django.contrib import admin
from .models import (
    Event,
    EventType,
)

admin.site.register(EventType)
admin.site.register(Event)
