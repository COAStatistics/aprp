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
    Festival,
    FestivalName,
    AbstractProduct,
    Last5YearsItems,
)
import json

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


class FestivalReport(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/festival-report.html'
    # roc_year_sel='all'

    def post(self, request, **kwargs):
        self.kwargs['POST'] = request.POST
        self.roc_year_sel=self.kwargs['POST']['roc_year_sel']
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(FestivalReport, self).get_context_data(**kwargs)
        #節日名稱       
        festival_list = FestivalName.objects.filter(enable=True).order_by('id')        
        context['festival_list'] = festival_list
        #年度
        roc_year_set = set()
        for y in Festival.objects.values('roc_year'):
            roc_year_set.add(y['roc_year'])
        context['roc_year_list'] = sorted(roc_year_set,reverse=True)
        #自選農產品清單
        item_list = AbstractProduct.objects.filter(type=1,track_item=True) | AbstractProduct.objects.filter(id__range = [130001,130005],type=2,track_item=True) | AbstractProduct.objects.filter(id__range = [90008,90016],type=2,track_item=True) | AbstractProduct.objects.filter(id__range = [100004,100006],type=2,track_item=True) | AbstractProduct.objects.filter(id__range = [110003,110006],type=2,track_item=True) #批發品項+產地(牛5,雞8,鴨3,鵝4)

        context['item_list'] = item_list
        return context


class Last5YearsReport(LoginRequiredMixin, TemplateView):
    redirect_field_name = 'redirect_to'
    template_name = 'ajax/last5years-report.html'

    def post(self, request, **kwargs):
        self.kwargs['POST'] = request.POST
        self.roc_year_sel=self.kwargs['POST']['item_id_list']
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(Last5YearsReport, self).get_context_data(**kwargs)
        #品項       
        items_list = Last5YearsItems.objects.filter(enable=True).order_by('id')
        items_list = self.sort_item_list(items_list)
        all_items = {}
        for i in items_list:
            pid_list = []
            source_list = []
            pids = i.product_id.all()
            sources = i.source.all()
            for p in pids:
                pid_list.append(str(p.id))
            for s in sources:
                source_list.append(str(s.id))
            pid = ','.join(pid_list)
            source = ','.join(source_list)
            
            all_items[i.name] = {'product_id':pid,'source':source}

        context['items_list'] = all_items
        return context

    def sort_item_list(self, items_list):
        items_dic = {item.name: (item, item.product_id.first().id) for item in items_list}
        sorted_items = sorted(items_dic.items(), key=lambda x: x[1][1])
        sub_items = sorted_items[13:35]
        del sorted_items[13:35]
        sorted_items = sorted_items[:7] + sub_items + sorted_items[7:]
        sub_items = sorted_items[30:35]
        del sorted_items[30:35]
        sorted_items = sorted_items[:21] + sub_items + sorted_items[21:]
        sub_items = sorted_items[9:11]
        del sorted_items[9:11]
        sorted_items = sorted_items[:64] + sub_items + sorted_items[64:]
        sorted_items.insert(65, sorted_items.pop(32))
        sub_items = sorted_items[:2]
        del sorted_items[:2]
        sorted_items = sorted_items[:68] + sub_items + sorted_items[68:]

        return [item[1][0] for item in sorted_items]

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
