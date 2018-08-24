from django.conf.urls import url, include
from .views import post_list, post_create, post_update, post_delete

urlpatterns = [
    url(r'^list/$', post_list, name='post_list'),
    url(r'^create/$', post_create, name='post_create'),
    url(r'^(?P<pk>\d+)/update/$', post_update, name='post_update'),
    url(r'^(?P<pk>\d+)/delete/$', post_delete, name='post_delete'),
    url(r'^api/', include('posts.api.urls'), name='api'),
]