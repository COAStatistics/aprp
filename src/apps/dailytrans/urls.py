from django.conf.urls import url
from .views import (
    render_daily_report,
    render_festival_report,
    render_last5years_report,
)

urlpatterns = [
    url(r'^daily-report/render/', render_daily_report, name='render_daily_report'),
    url(r'^festival-report/render/', render_festival_report, name='render_festival_report'),
    url(r'^last5years-report/render/', render_last5years_report, name='render_last_5_years_report'),
]
