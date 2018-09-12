from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.CommentListAllAPIView.as_view(), name='api_comments_all'),
    url(r'^create$', views.CommentCreateAPIView.as_view(), name='api_comments_c'),
]
