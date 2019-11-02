from django.conf.urls import url
from .views import (
    render_daily_report
)

urlpatterns = [
    url(r'^daily-report/render/', render_daily_report, name='render_daily_report'),
]

