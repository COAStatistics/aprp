from django.conf.urls import url, include

urlpatterns = [
    url(r'^ajax/', include('configs.ajax.urls', namespace='ajax')),
]