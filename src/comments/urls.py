from django.conf.urls import url, include

urlpatterns = [
    # url(r'^create/$', comment_create, name='comment_create'),
    # url(r'^(?P<pk>\d+)/update/$', comment_update, name='comment_update'),
    # url(r'^(?P<pk>\d+)/delete/$', comment_delete, name='comment_delete'),

    url(r'^api/', include('comments.api.urls'), name='api_comment'),
]
