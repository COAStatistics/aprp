from django.conf.urls import url, include

urlpatterns = [
    url(r'^ajax/', include('apps.configs.ajax.urls', namespace='ajax')),
]
