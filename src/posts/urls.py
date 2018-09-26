from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.post_socialwall, name='post_socialwall'),
    url(r'^newform$', views.post_new_form, name='post_new_form'),
    url(r'^search$', views.post_search, name='post_search'),
    url(r'^api/', include('posts.api.urls'), name='api_post'),
]
