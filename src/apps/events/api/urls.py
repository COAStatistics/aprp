from django.conf.urls import url
from tagulous.views import autocomplete
from .views import (
    EventTypeListCreateAPIView,
    EventTypeRetrieveUpdateDestroyAPIView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
)
from apps.events.models import EventType


urlpatterns = [
    url(r'^eventtype/(?P<pk>\d+)/$', EventTypeRetrieveUpdateDestroyAPIView.as_view(), name='api_eventtype_rud'),
    url(r'^event/(?P<pk>\d+)/$', EventRetrieveUpdateDestroyAPIView.as_view(), name='api_event_rud'),
    url(r'^eventtype/$', EventTypeListCreateAPIView.as_view(), name='api_eventtype_cr'),
    url(r'^event/$', EventListCreateAPIView.as_view(), name='api_event_cr'),
    # You can also pass in a QuerySet of the tag model
    url(r'^event-autocomplete/$', autocomplete, {'tag_model': EventType.objects.order_by('level')}, name='event_type_autocomplete'),
]
