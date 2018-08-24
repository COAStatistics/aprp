from django.conf.urls import url
from .views import comment_create, comment_update, comment_delete

urlpatterns = [
    url(r'^create/$', comment_create, name='comment_create'),
    url(r'^(?P<pk>\d+)/update/$', comment_update, name='comment_update'),
    url(r'^(?P<pk>\d+)/delete/$', comment_delete, name='comment_delete'),
]