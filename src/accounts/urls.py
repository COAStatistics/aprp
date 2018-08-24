from django.conf.urls import url, include
from .views import (
    login_view,
    logout_view,
    register_view,
    forgot_password_view,
    reset_password_view,
    user_activate,
    reset_email_view,
    activation_resend_view,
)

urlpatterns = [
    url(r'^login/', login_view, name='login'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^register/', register_view, name='register'),
    url(r'^forgot-password/', forgot_password_view, name='forgot_password'),
    url(r'^register-resend/', activation_resend_view, name='activation_resend'),
    url(r'^reset-password/(?P<key>[a-z0-9].*)/$', reset_password_view, name='reset_password'),
    url(r'^reset-email/(?P<key>[a-z0-9].*)/$', reset_email_view, name='reset_email'),
    url(r'^activate/(?P<key>[a-z0-9].*)/$', user_activate, name='activate'),
]
