from django.views.generic.base import TemplateView
from django.http import JsonResponse
from django.conf import settings
from django.utils import translation
from django.shortcuts import (
    redirect,
)
from functools import wraps
from .utils import (
    jarvismenu_extra_context,
    product_selector_ui_extra_context,
    watchlist_base_chart_tab_extra_context,
    chart_tab_extra_context,
    watchlist_base_chart_contents_extra_context,
    product_selector_base_extra_context,
    watchlist_base_integration_extra_context,
    product_selector_base_integration_extra_context,
)
from apps.watchlists.models import Watchlist
from apps.configs.models import (
    Config,
    Chart,
    Type,
)


def login_required(view):
    """
    Custom login_required to handle ajax request
    Check user is login and is_active
    """
    @wraps(view)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.is_active:
            if request.is_ajax():
                # if is ajax return 403
                return JsonResponse({'login_url': settings.LOGIN_URL}, status=403)
            else:
                # if not ajax redirect login page
                return redirect(settings.LOGIN_URL)
        return view(request, *args, **kwargs)
    return inner


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwds):
        return login_required(super().as_view(**kwds))


class BrowserNotSupport(TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'browser-not-support.html'


class Index(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        user_language = kwargs.get('lang')
        translation.activate(user_language)
        request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        return super(Index, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)

        # watchlist options use for watchlist shortcut render
        watchlists = Watchlist.objects.order_by('id').all()

        if not self.request.user.info.watchlist_viewer:
            watchlists = watchlists.exclude(watch_all=True)

        context['watchlists'] = watchlists

        # filter watchlist item or use default
        # watchlist_id = kwargs.get('wi') or self.request.COOKIES.get('aprp_userwatchlistid')
        watchlist_id = kwargs.get('wi')
        watchlist = Watchlist.objects.filter(id=watchlist_id).first()
        if not watchlist:
            watchlist = Watchlist.objects.get(is_default=True)
        context['user_watchlist'] = watchlist

        # classify config into different folder manually
        configs = watchlist.related_configs()
        context['totals'] = configs.filter(id__in=[2, 3, 4])  # render configs
        context['agricultures'] = configs.filter(id__in=[1, 5, 6, 7])  # render configs
        context['livestocks'] = configs.filter(id__in=[8, 9, 10, 11, 12, 14])  # render configs
        if configs.filter(id=13).first():  # render products, config as folder
            context['fisheries'] = configs.get(id=13).first_level_products(watchlist=watchlist)

        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(Index, self).render_to_response(context, **response_kwargs)
        # set cookie
        # watchlist = context['user_watchlist']
        # response.set_cookie('aprp_userwatchlistid', watchlist.id)
        return response


class About(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/about.html'


class DailyReport(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/daily-report.html'


class ProductSelector(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/product-selector.html'

    def get_context_data(self, **kwargs):
        context = super(ProductSelector, self).get_context_data(**kwargs)
        context['configs'] = Config.objects.order_by('id')
        context['types'] = Type.objects.order_by('id')
        return context


class ProductSelectorUI(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/product-selector-ui.html'

    def post(self, request, **kwargs):
        self.kwargs['POST'] = request.POST
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(ProductSelectorUI, self).get_context_data(**kwargs)
        extra_context = product_selector_ui_extra_context(self)
        context.update(extra_context)
        return context


class JarvisMenu(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/jarvismenu.html'

    def get_context_data(self, **kwargs):
        context = super(JarvisMenu, self).get_context_data(**kwargs)
        extra_context = jarvismenu_extra_context(self)
        context.update(extra_context)
        return context


class ChartTabs(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/chart-tab.html'
    watchlist_base = False

    def get_context_data(self, **kwargs):
        context = super(ChartTabs, self).get_context_data(**kwargs)
        if self.watchlist_base:
            extra_context = watchlist_base_chart_tab_extra_context(self)
        else:
            extra_context = chart_tab_extra_context(self)
        context.update(extra_context)
        return context


class ChartContents(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    no_data = False  # custom
    watchlist_base = False
    product_selector_base = False

    def get_template_names(self):
        if self.no_data:
            return 'ajax/no-data.html'
        else:
            chart_id = self.kwargs.get('ci')
            chart = Chart.objects.get(id=chart_id)
            return chart.template_name

    def post(self, request, **kwargs):
        self.kwargs['POST'] = request.POST
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(ChartContents, self).get_context_data(**kwargs)
        if self.watchlist_base:
            extra_context = watchlist_base_chart_contents_extra_context(self)
            context.update(extra_context)
        elif self.product_selector_base:
            extra_context = product_selector_base_extra_context(self)
            context.update(extra_context)

        # no data checking, if series_options is empty, render no-data template
        if not context['series_options']:
            self.no_data = True

        return context


class IntegrationTable(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    no_data = False  # custom
    to_init = True  # custom  # default is True
    watchlist_base = False
    product_selector_base = False

    def get_template_names(self):
        # set template_name if no assign yet

        if self.no_data:
            return 'ajax/no-data.html'

        if self.to_init:
            return 'ajax/integration-panel.html'
        else:
            return 'ajax/integration-row.html'

    def post(self, request, **kwargs):
        self.kwargs['POST'] = request.POST
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(IntegrationTable, self).get_context_data(**kwargs)
        if self.watchlist_base:
            extra_context = watchlist_base_integration_extra_context(self)
            context.update(extra_context)
        elif self.product_selector_base:
            extra_context = product_selector_base_integration_extra_context(self)
            context.update(extra_context)

        # no data checking, if series_options or option is empty, render no-data template
        if self.to_init:
            if not context['series_options']:
                self.no_data = True
        else:
            if not context['option']:
                self.no_data = True

        return context
