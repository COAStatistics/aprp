from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.PostListAPIView.as_view(), name='api_socialwall')
]
