from django.conf.urls import url
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
]
