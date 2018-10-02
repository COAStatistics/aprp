from django.conf.urls import url
from tagulous.views import autocomplete
from .views import (
    EventTypeListCreateAPIView,
    EventTypeRetrieveUpdateDestroyAPIView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
)
from events.models import EventType


urlpatterns = [
    url(r'^eventtype/(?P<pk>\d+)/$', EventTypeRetrieveUpdateDestroyAPIView.as_view(), name='api_eventtype_rud'),
    url(r'^event/(?P<pk>\d+)/$', EventRetrieveUpdateDestroyAPIView.as_view(), name='api_event_rud'),
    url(r'^eventtype/$', EventTypeListCreateAPIView.as_view(), name='api_eventtype_cr'),
    url(r'^event/$', EventListCreateAPIView.as_view(), name='api_event_cr'),
    url(r'^event-autocomplete/$', autocomplete, {'tag_model': EventType}, name='event_type_autocomplete'),
]


