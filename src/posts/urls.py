from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.post_socialwall, name='post_socialwall'),

    url(r'^api/', include('posts.api.urls'), name='api'),
]
