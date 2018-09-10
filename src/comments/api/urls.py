from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^all$', views.CommentListAllAPIView.as_view(), name='api_comments_all'),
]
