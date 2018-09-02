import datetime
from watchlists.models import (
    Watchlist,
    MonitorProfile,
)
from dailytrans.utils import (
    get_daily_price_volume,
    get_daily_price_by_year,
    get_monthly_price_distribution,
    get_integration,
)
from configs.models import (
    Config, AbstractProduct, Source, Type, Chart,
)
from configs.api.serializers import UnitSerializer
from watchlists.api.serializers import MonitorProfileSerializer


def jarvismenu_extra_context(instance):
    """
    A function return extra context work for JarvisMenu CBV and other view with arguments wi, ct, oi, lct, loi

    wi(watchlist id) allows: integer
    ct(content type) allows: 'config', 'type', 'product', 'source'
    oi(object id) allows: integer
    lct(last content type) allows: 'config', 'type', 'product', 'source'
    loi(last object id) allows: integer
    """
    kwargs = instance.kwargs
    user = instance.request.user

    extra_context = dict()

    watchlist_id = kwargs.get('wi')
    content_type = kwargs.get('ct')
    object_id = kwargs.get('oi')
    last_content_type = kwargs.get('lct')
    last_object_id = kwargs.get('loi')

    watchlist = Watchlist.objects.get(id=watchlist_id)
    extra_context['watchlist'] = watchlist

    if content_type == 'config':
        config = Config.objects.get(id=object_id)
        products = config.first_level_products(watchlist=watchlist)
        if products:
            extra_context['items'] = products
            extra_context['ct'] = 'product'
            extra_context['lct'] = 'config'
            extra_context['loi'] = object_id

    elif content_type == 'type':
        if last_content_type == 'product':
            product = AbstractProduct.objects.get(id=last_object_id)

            if product.has_child:
                extra_context['items'] = product.children(watchlist=watchlist).filter(type__id=object_id)
                extra_context['ct'] = 'product'
                extra_context['lct'] = 'type'
                extra_context['loi'] = object_id

            elif product.has_source:

                extra_context['items'] = product.sources(watchlist=watchlist)
                extra_context['ct'] = 'source'
                extra_context['lct'] = 'product'
                extra_context['loi'] = product.id

    elif content_type == 'product':
        product = AbstractProduct.objects.get(id=object_id)
        extra_context['lct'] = 'product'
        extra_context['loi'] = product.id

        if product.level == product.config.type_level and not user.info.is_editor:
            pass

        elif product.types(watchlist=watchlist).count() > 1:
            extra_context['items'] = product.types(watchlist=watchlist)
            extra_context['ct'] = 'type'

        elif product.has_child:
            extra_context['items'] = product.children(watchlist=watchlist)
            extra_context['ct'] = 'product'

        elif product.has_source:
            extra_context['items'] = product.sources(watchlist=watchlist)
            extra_context['ct'] = 'source'

    return extra_context


def chart_tab_extra_context(instance):
    kwargs = instance.kwargs
    extra_context = dict()

    content_type = kwargs.get('ct')
    object_id = kwargs.get('oi')
    last_content_type = kwargs.get('lct')
    last_object_id = kwargs.get('loi')
    watchlist_id = kwargs.get('wi')
    watchlist = Watchlist.objects.get(id=watchlist_id)
    extra_context['watchlist'] = watchlist

    if content_type == 'config':
        config = Config.objects.get(id=object_id)
        extra_context['charts'] = config.charts.all()
    elif content_type == 'product':
        product = AbstractProduct.objects.get(id=object_id)
        extra_context['charts'] = product.config.charts.all()
        monitor_profiles = MonitorProfile.objects.filter(product__id=object_id, watchlist__id=watchlist_id).order_by('price')

        extra_context['product'] = product
        extra_context['types'] = product.types(watchlist=watchlist)
        extra_context['monitor_profiles'] = monitor_profiles
        current_month = datetime.date.today().month
        current_monitor_profiles = monitor_profiles.filter(months__in=[current_month])
        extra_context['current_monitor_profiles'] = MonitorProfileSerializer(current_monitor_profiles, many=True).data

    elif content_type in ['type', 'source']:
        if last_content_type == 'product':
            product = AbstractProduct.objects.get(id=last_object_id)
            extra_context['charts'] = product.config.charts.all()

    return extra_context


def chart_contents_extra_context(instance):
    kwargs = instance.kwargs

    extra_context = dict()

    chart_id = kwargs.get('ci')
    watchlist_id = kwargs.get('wi')
    content_type = kwargs.get('ct')
    object_id = kwargs.get('oi')
    last_content_type = kwargs.get('lct')
    last_object_id = kwargs.get('loi')

    # post data
    selected_years = kwargs.get('selected_years')

    watchlist = Watchlist.objects.get(id=watchlist_id)

    # selected sources
    sources = None

    # filter items & types
    if content_type == 'config':
        items = watchlist.children().filter(product__config__id=object_id)

    elif content_type == 'type':
        if last_content_type == 'product':
            items = watchlist.children().filter_by_product(product__id=last_object_id)

    elif content_type == 'product':
        items = watchlist.children().filter_by_product(product__id=object_id)

    elif content_type == 'source':
        items = watchlist.children().filter_by_product(product__id=last_object_id)
        sources = Source.objects.filter(id=object_id)

    types = Type.objects.filter_by_watchlist_items(watchlist_items=items)
    if content_type == 'type':
        types = types.filter(id=object_id)

    extra_context['unit_json'] = UnitSerializer(items.get_unit()).data

    # get tran data by chart
    series_options = []

    if chart_id in ['1', '2']:
        for t in types:
            end_date = datetime.date.today() if chart_id == '1' else None
            start_date = end_date + datetime.timedelta(days=-13) if chart_id == '1' else None
            option = get_daily_price_volume(_type=t,
                                            items=items.filter(product__type=t),
                                            sources=sources,
                                            start_date=start_date,
                                            end_date=end_date)
            if not option['no_data']:
                series_options.append(option)

    if chart_id == '3':
        for t in types:
            option = get_daily_price_by_year(_type=t,
                                             items=items.filter(product__type=t),
                                             sources=sources)
            if not option['no_data']:
                series_options.append(option)

    if chart_id == '4':
        extra_context['method'] = instance.request.method
        extra_context['selected_years'] = selected_years

        for t in types:
            option = get_monthly_price_distribution(_type=t,
                                                    items=items.filter(product__type=t),
                                                    sources=sources,
                                                    selected_years=selected_years)
            if not option['no_data']:
                series_options.append(option)

    extra_context['series_options'] = series_options
    extra_context['chart'] = Chart.objects.get(id=chart_id)

    return extra_context


def integration_extra_context(instance):
    kwargs = instance.kwargs

    extra_context = dict()

    chart_id = kwargs.get('ci')
    watchlist_id = kwargs.get('wi')
    content_type = kwargs.get('ct')
    object_id = kwargs.get('oi')
    last_content_type = kwargs.get('lct')
    last_object_id = kwargs.get('loi')

    # post data
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    type_id = kwargs.get('type_id')

    # get tran data by chart
    series_options = []

    watchlist = Watchlist.objects.get(id=watchlist_id)

    # selected sources
    sources = None

    # filter items & types
    if content_type == 'config':
        items = watchlist.children().filter(product__config__id=object_id)

    elif content_type == 'type':
        if last_content_type == 'product':
            items = watchlist.children().filter_by_product(product__id=last_object_id)

    elif content_type == 'product':
        items = watchlist.children().filter_by_product(product__id=object_id)

    elif content_type == 'source':
        items = watchlist.children().filter_by_product(product__id=last_object_id)
        sources = Source.objects.filter(id=object_id)

    extra_context['unit_json'] = UnitSerializer(items.get_unit()).data

    if instance.to_init:

        types = Type.objects.filter_by_watchlist_items(watchlist_items=items)
        if content_type == 'type':
            types = types.filter(id=object_id)

        for t in types:
            option = get_integration(_type=t,
                                     items=items.filter(product__type=t),
                                     sources=sources,
                                     start_date=start_date,
                                     end_date=end_date,
                                     to_init=True)
            if not option['no_data']:
                series_options.append(option)

        # datetime format
        formatter = '%m/%d' if start_date.year == end_date.year else '%Y/%m/%d'

        extra_context['start_date_format'] = start_date.strftime(formatter)
        extra_context['end_date_format'] = end_date.strftime(formatter)
        extra_context['chart'] = Chart.objects.get(id=chart_id)

    else:
        t = Type.objects.get(id=type_id)

        option = get_integration(_type=t,
                                 items=items.filter(product__type=t),
                                 sources=sources,
                                 start_date=start_date,
                                 end_date=end_date,
                                 to_init=False)
        if not option['no_data']:
            extra_context['option'] = option

    extra_context['series_options'] = series_options
    return extra_context


