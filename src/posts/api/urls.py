from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.PostListAllAPIView.as_view(), name='api_socialwall_all'),
    url(r'^create$', views.PostCreateAPIView.as_view(), name='api_socialwall_c'),
    url(r'^(?P<pk>\d+)$', views.PostRetrieveUpdateDestroyAPIView.as_view(), name='api_socialwall_rud'),
]
