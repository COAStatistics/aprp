"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import javascript_catalog
from .views import (
    Index,
    About,
    DailyReport,
    ProductSelector,
    ProductSelectorUI,
    JarvisMenu,
    ChartTabs,
    ChartContents,
    IntegrationTable,
    BrowserNotSupport,
    FestivalReport,
    Last5YearsReport,
)

urlpatterns = [
    # local apps
    url(r'^accounts/', include('apps.accounts.urls', namespace='accounts')),
    url(r'^posts/', include('apps.posts.urls', namespace='posts')),
    url(r'^comments/', include('apps.comments.urls', namespace='comments')),
    url(r'^events/', include('apps.events.urls', namespace='events')),
    url(r'^dailytrans/', include('apps.dailytrans.urls', namespace='dailytrans')),
    # i18n
    url(r'^jsi18n/$', javascript_catalog, name='parse_javascript'),
    url(r'^set-user-language/(?P<lang>[-\w]+)/$', Index.as_view(), name='set_user_language'),
    # third part
    url(r'^tracking/', include('tracking.urls')),
    # watchlist
    url(r'^set-user-watchlist/(?P<wi>\d+)/$', Index.as_view(), name='set_user_watchlist'),
]

urlpatterns += i18n_patterns(
    # admin
    url(r'^{}/'.format(settings.DJANGO_ADMIN_PATH), admin.site.urls),
    # pages
    url(r'^$', Index.as_view(), name='index'),
    url(r'^about/', About.as_view(), name='about'),
    url(r'^browser-not-support/', BrowserNotSupport.as_view(), name='browser_not_support'),
    # jarvis menu ajax
    url(r'^jarvismenu/(?P<wi>\d+)/(?P<ct>\w+)/(?P<oi>\d+)/$', JarvisMenu.as_view(), name='jarvismenu'),
    url(r'^jarvismenu/(?P<wi>\d+)/(?P<ct>\w+)/(?P<oi>\d+)/(?P<lct>\w+)/(?P<loi>\d+)/$', JarvisMenu.as_view(), name='jarvismenu'),
    # chart tab ajax
    url(r'^chart-tab/chart/$', ChartTabs.as_view(), name='chart_tab'),
    url(r'^chart-tab/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/$',
        ChartTabs.as_view(watchlist_base=True), name='chart_tab'),
    url(r'^chart-tab/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/sub-resource/(?P<lct>\w+)-(?P<loi>\d+)/$',
        ChartTabs.as_view(watchlist_base=True), name='chart_tab'),
    # chart content ajax
    url(r'^chart-content/chart/(?P<ci>\d+)/type/(?P<type>\d+)/products/(?P<products>\w+)/$',
        ChartContents.as_view(product_selector_base=True), name='chart_content'),
    url(r'^chart-content/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)/(?P<oi>\d+)/$',
        ChartContents.as_view(watchlist_base=True), name='chart_content'),
    url(r'^chart-content/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/sub-resource/(?P<lct>\w+)-(?P<loi>\d+)/$',
        ChartContents.as_view(watchlist_base=True), name='chart_content'),
    # chart content ajax
    url(r'^integration-table/chart/(?P<ci>\d+)/type/(?P<type>\d+)/products/(?P<products>\w+)/$',
        IntegrationTable.as_view(product_selector_base=True), name='integration_table'),
    url(r'^integration-table/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/$',
        IntegrationTable.as_view(watchlist_base=True), name='integration_table'),
    url(r'^integration-table/chart/(?P<ci>\d+)/watchlist/(?P<wi>\d+)/resource/(?P<ct>\w+)-(?P<oi>\d+)/sub-resource/(?P<lct>\w+)-(?P<loi>\d+)/$',
        IntegrationTable.as_view(watchlist_base=True), name='integration_table'),
    # daily report ajax
    url(r'^daily-report/', DailyReport.as_view(), name='daily_report'),
    # festival report ajax
    url(r'^festival-report/', FestivalReport.as_view(), name='festival_report'),
    url(r'^last5years-report/', Last5YearsReport.as_view(), name='last5years_report'),
    # product selector
    url(r'^product-selector/$', ProductSelector.as_view(), name='product_selector'),
    url(r'^product-selector-ui/step/(?P<step>\d+)/$', ProductSelectorUI.as_view(), name='product_selector_ui'),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SERVE_MEDIA_FILES:
    urlpatterns += patterns(
        '',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
