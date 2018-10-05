import time
import operator
import datetime
from django.db.models.expressions import RawSQL

from pandas import DataFrame
from collections import OrderedDict
from functools import reduce

from django.utils.translation import ugettext as _
from django.db.models import Q
from django.db.models import Sum, Avg, F, Count, Func, IntegerField

from dailytrans.models import DailyTran
from configs.api.serializers import TypeSerializer


def get_query_set(_type, items, sources=None):
    """
    :param _type: Type object
    :param items: WatchlistItem objects
    :param sources: Source objects  # optional
    :return: <QuerySet>
    """

    if not items:
        return DailyTran.objects.none()

    if sources:
        query = reduce(
            operator.or_,
            ((Q(product=item.product) & Q(source__in=sources)) for item in items)
        )
    else:
        query = reduce(
            operator.or_,
            (
                (Q(product=item.product) & Q(source__in=item.sources.all())) if item.sources.all() else
                (Q(product=item.product)) for item in items)
        )

    return DailyTran.objects.filter(product__type=_type).filter(query)


def get_group_by_date_query_set(query_set, start_date=None, end_date=None, specific_year=True):
    """
    :param query_set: Query before annotation
    :param start_date: <Date>
    :param end_date: <Date>
    :param specific_year: To filter query_set with date__range else filter with manager method to exclude year
    :return: Query after annotation
    """

    # The count() might be different while queue running and storing new data
    if query_set.count():
        has_volume = query_set.filter(volume__isnull=False).count() / query_set.count() > 0.8
        has_weight = query_set.filter(avg_weight__isnull=False).count() / query_set.count() > 0.8
    else:
        has_volume = False
        has_weight = False

    # Date filters
    if isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date):
        if specific_year:
            query_set = query_set.filter(date__range=[start_date, end_date])
        else:
            query_set = query_set.between_month_day_filter(start_date, end_date)

    query_set = (query_set.values('date').annotate(
        year=Year('date'),
        month=Month('date'),
        day=Day('date')))

    if has_volume and has_weight:

        q = (query_set.annotate(
                avg_price=Sum(F('avg_price') * F('volume') * F('avg_weight')) / Sum(F('volume') * F('avg_weight')),
                sum_volume=Sum(F('volume')),
                avg_avg_weight=Sum(F('avg_weight') * F('volume')) / Sum(F('volume')),
                source_count=Count('source', distinct=True)))  # for hog

    elif has_volume:

        q = (query_set.annotate(
                avg_price=Sum(F('avg_price') * F('volume')) / Sum('volume'),
                sum_volume=Sum('volume')))

    else:

        q = (query_set.annotate(avg_price=Avg('avg_price')).order_by('date'))

    # Order by date
    q = q.order_by('date')

    return q, has_volume, has_weight


def get_daily_price_volume(_type, items, sources=None, start_date=None, end_date=None):

    query_set = get_query_set(_type, items, sources)

    q, has_volume, has_weight = get_group_by_date_query_set(query_set, start_date, end_date)

    if q:
        # create empty date list
        start_date = start_date or q.first()['date']
        end_date = end_date or q.last()['date']
        diff = end_date - start_date
        date_list = [start_date + datetime.timedelta(days=x) for x in range(0, diff.days + 1)]

        if has_volume and has_weight:

            raw_data = {
                'columns': [
                    {'value': _('Date'), 'format': 'date'},
                    {'value': _('Average Price'), 'format': 'avg_price'},
                    {'value': _('Sum Volume'), 'format': 'sum_volume'},
                    {'value': _('Average Weight'), 'format': 'avg_avg_weight'}
                ],
                'rows': [[dic['date'], dic['avg_price'], dic['sum_volume'], dic['avg_avg_weight']] for
                         dic in q]
            }

            missing_point_data = OrderedDict((date, [None, None, None]) for date in date_list)
            for dic in q:
                missing_point_data[dic['date']][0] = dic['avg_price']
                missing_point_data[dic['date']][1] = dic['sum_volume']
                missing_point_data[dic['date']][2] = dic['avg_avg_weight']

            highchart_data = {
                'avg_price': [[to_unix(date), value[0]] for date, value in missing_point_data.items()],
                'sum_volume': [[to_unix(date), value[1]] for date, value in missing_point_data.items()],
                'avg_weight': [[to_unix(date), value[2]] for date, value in missing_point_data.items()],
            }

        elif has_volume:

            raw_data = {
                'columns': [
                    {'value': _('Date'), 'format': 'date'},
                    {'value': _('Average Price'), 'format': 'avg_price'},
                    {'value': _('Sum Volume'), 'format': 'sum_volume'}
                ],
                'rows': [[dic['date'], dic['avg_price'], dic['sum_volume']] for dic in q]
            }

            missing_point_data = OrderedDict((date, [None, None]) for date in date_list)
            for dic in q:
                missing_point_data[dic['date']][0] = dic['avg_price']
                missing_point_data[dic['date']][1] = dic['sum_volume']

            highchart_data = {
                'avg_price': [[to_unix(date), value[0]] for date, value in missing_point_data.items()],
                'sum_volume': [[to_unix(date), value[1]] for date, value in missing_point_data.items()],
            }

        else:

            raw_data = {
                'columns': [
                    {'value': _('Date'), 'format': 'date'},
                    {'value': _('Average Price'), 'format': 'avg_price'}
                ],
                'rows': [[dic['date'], dic['avg_price']] for dic in q]
            }

            missing_point_data = OrderedDict((date, [None]) for date in date_list)
            for dic in q:
                missing_point_data[dic['date']][0] = dic['avg_price']

            highchart_data = {
                'avg_price': [[to_unix(date), value[0]] for date, value in missing_point_data.items()],
            }

        response_data = {
            'type': TypeSerializer(_type).data,
            'highchart': highchart_data,
            'raw': raw_data,
            'no_data': len(highchart_data['avg_price']) == 0,
        }
    else:
        response_data = {
            'no_data': True
        }

    return response_data


def get_daily_price_by_year(_type, items, sources=None):

    def get_result(key):
        # Get years
        years = [date.year for date in query_set.dates('date', 'year')]

        # Create date_list
        base = datetime.date(2016, 1, 1)
        date_list = [base + datetime.timedelta(days=x) for x in range(0, 366)]

        result = {year: OrderedDict(((date, None) for date in date_list)) for year in years}

        # Fill daily price to result
        for dic in q:
            date = datetime.date(year=2016, month=dic['date'].month, day=dic['date'].day)

            result[dic['date'].year][date] = dic[key]

        for year, obj in result.items():
            result[year] = [[to_unix(date), value] for date, value in obj.items()]

        # Transform result
        if q:
            raw_data_rows = [[date] for date in date_list]

            for year in years:
                for i, obj in enumerate(result[year]):
                    value = obj[1] if obj[1] else ''
                    raw_data_rows[i].append(value)

            def all_empty(lst):
                empty_count = 0
                for val in lst:
                    if val == '':
                        empty_count += 1
                return empty_count == len(lst)

            # Remove row when all value is empty
            raw_data_rows_remove_empty = [row for row in raw_data_rows if not all_empty(row[1:])]

            raw_data_columns = [{'value': _('Date'), 'format': 'date'}]
            raw_data_columns.extend([{'value': str(year), 'format': key} for year in years])

            raw_data = {
                'columns': raw_data_columns,
                'rows': raw_data_rows_remove_empty
            }
        else:
            raw_data = None

        return {
            'highchart': result,
            'raw': raw_data,
        }

    query_set = get_query_set(_type, items, sources)

    q, has_volume, has_weight = get_group_by_date_query_set(query_set)

    response_data = dict()

    response_data['years'] = [date.year for date in query_set.dates('date', 'year')]

    response_data['type'] = TypeSerializer(_type).data

    response_data['price'] = get_result('avg_price')

    if has_volume:
        response_data['volume'] = get_result('sum_volume') if has_volume else None

    if has_weight:
        response_data['weight'] = get_result('avg_avg_weight') if has_weight else None

    response_data['no_data'] = len(response_data['price']['highchart'].keys()) == 0

    return response_data


def annotate_avg_price(df, key):
    def by_weight_volume(group):
        avg_price = group['avg_price']
        sum_volume = group['sum_volume']
        avg_avg_weight = group['avg_avg_weight']
        return (avg_price * sum_volume * avg_avg_weight).sum() / (sum_volume * avg_avg_weight).sum()

    def by_volume(group):
        avg_price = group['avg_price']
        sum_volume = group['sum_volume']
        return (avg_price * sum_volume).sum() / sum_volume.sum()

    grouped_df = df.groupby(key)
    if 'avg_avg_weight' in df and 'sum_volume' in df:
        price_series = grouped_df.apply(by_weight_volume)
        return price_series.T.to_dict()
    elif 'sum_volume' in df:
        price_series = grouped_df.apply(by_volume)
        return price_series.T.to_dict()
    else:
        return grouped_df.mean().to_dict().get('avg_price')


def annotate_avg_weight(df, key):
    def by_volume(group):
        sum_volume = group['sum_volume']
        avg_avg_weight = group['avg_avg_weight']
        return (sum_volume * avg_avg_weight).sum() / sum_volume.sum()

    grouped_df = df.groupby(key)
    if 'avg_avg_weight' in df and 'sum_volume' in df:
        weight_series = grouped_df.apply(by_volume)
        return weight_series.T.to_dict()
    else:
        return grouped_df.mean().to_dict().get('avg_avg_weight')


def get_monthly_price_distribution(_type, items, sources=None, selected_years=None):

    def get_result(key):
        highchart_data = {}
        raw_data = {}

        if q.count() > 0:
            df = DataFrame(list(q))

            s_quantile = df.groupby('month')[key].quantile([.0, .25, .5, .75, 1])
            if key == 'avg_price':
                price_dict = annotate_avg_price(df, 'month')
                s_mean = DataFrame(price_dict, index=[0]).loc[0]
            elif key == 'avg_avg_weight':
                weight_dict = annotate_avg_weight(df, 'month')
                s_mean = DataFrame(weight_dict, index=[0]).loc[0]
            else:
                s_mean = df.groupby('month')[key].mean()

            '''
            s_quantile.to_dict():
                {(1, 0.0): 5.95299909173479,
                 (1, 0.25): 6.986073757018829,
                 (1, 0.5): 9.42770805812417,
                 (1, 0.75): 12.4538909161054,
                 (1, 1.0): 22.6906077008242, ...}

            s_quantile.index.levels[0]: 
                Int64Index([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], dtype='int64', name='month')
            '''

            highchart_data = {
                'perc_0': [[key[0], value] for key, value in s_quantile.iteritems() if key[1] == 0.0],
                'perc_25': [[key[0], value] for key, value in s_quantile.iteritems() if key[1] == 0.25],
                'perc_50': [[key[0], value] for key, value in s_quantile.iteritems() if key[1] == 0.5],
                'perc_75': [[key[0], value] for key, value in s_quantile.iteritems() if key[1] == 0.75],
                'perc_100': [[key[0], value] for key, value in s_quantile.iteritems() if key[1] == 1.0],
                'mean': [[key, value] for key, value in s_mean.iteritems()],
                'years': years
            }

            raw_data = {
                'columns': [
                    {'value': _('Month'), 'format': 'integer'},
                    {'value': _('Min'), 'format': key},
                    {'value': _('25%'), 'format': key},
                    {'value': _('50%'), 'format': key},
                    {'value': _('75%'), 'format': key},
                    {'value': _('Max'), 'format': key},
                    {'value': _('Mean'), 'format': key},
                ],
                'rows': [[i, s_quantile.loc[i][0.0],
                          s_quantile.loc[i][0.25],
                          s_quantile.loc[i][0.5],
                          s_quantile.loc[i][0.75],
                          s_quantile.loc[i][1],
                          s_mean.loc[i]] for i in s_quantile.index.levels[0]]
            }

        return {
            'highchart': highchart_data,
            'raw': raw_data,
        }

    query_set = get_query_set(_type, items, sources)

    years = [date.year for date in query_set.dates('date', 'year')]

    if selected_years:
        query_set = query_set.filter(date__year__in=selected_years)

    q, has_volume, has_weight = get_group_by_date_query_set(query_set)

    response_data = dict()
    response_data['type'] = TypeSerializer(_type).data

    response_data['years'] = years

    response_data['price'] = get_result('avg_price')

    if has_volume:
        response_data['volume'] = get_result('sum_volume')

    if has_weight:
        response_data['weight'] = get_result('avg_avg_weight')

    response_data['no_data'] = len(response_data['price']['highchart'].keys()) == 0

    return response_data


def get_integration(_type, items, start_date, end_date, sources=None, to_init=True):
    """
    :param _type: Type object
    :param items: AbstractProduct objects
    :param start_date: datetime object
    :param end_date: datetime object
    :param sources: Source objects
    :param to_init: to render table if true; to render rows if false
    :return:
    """
    def spark_point_maker(qs, add_unix=True):
        """
        :param qs: Query after annotation
        :param add_unix: To add a key "unix" in each query objects
        :return: List of point object
        """
        points = list(qs)
        if add_unix:
            for d in points:
                d['unix'] = to_unix(d['date'])

        return points

    def pandas_annotate_init(qs, hog_exception_condition):
        df = DataFrame(list(qs))
        series = df.mean()
        series = series.drop(['year', 'month', 'day'], axis=0)
        result = series.T.to_dict()

        # group by all rows by added column 'key'
        df['key'] = 'value'
        price_dict = annotate_avg_price(df, 'key')  # return {'value': price}
        # apply annotated price to result avg_price
        result['avg_price'] = price_dict['value']

        if hog_exception_condition:
            result['sum_volume'] = df.drop(df[df.source_count <= 10].index).mean().to_dict().get('sum_volume')

        return result

    def pandas_annotate_year(qs, hog_exception_condition):
        df = DataFrame(list(qs))
        df = df.groupby(['year'], as_index=False).mean()
        df = df.drop(['month', 'day'], axis=1)
        result = df.T.to_dict().values()
        # group by year
        price_dict = annotate_avg_price(df, 'year')  # return {2017: price1, 2018: price2}
        # apply annotated price to result avg_price
        for dic in result:
            year = dic['year']
            if year in price_dict:
                dic['avg_price'] = price_dict[year]

        if hog_exception_condition:
            new_df = DataFrame(list(qs))
            drop_source_lte10 = new_df.drop(new_df[new_df.source_count <= 10].index)
            drop_source_lte10 = drop_source_lte10.groupby(['year'], as_index=False).mean()
            new_result = drop_source_lte10.T.to_dict().values()

            result = new_result

        return result

    query_set = get_query_set(_type, items, sources)

    diff = end_date - start_date + datetime.timedelta(1)

    last_start_date = start_date - diff
    last_end_date = end_date - diff

    # ** Note: Hog sum volume exception **
    # ** See annotate field "source_count" in get_group_by_date_query_set **
    # ** single_search means single product(on _type) on single source
    ids = query_set.values_list('product__id', flat=True).distinct()
    hog_exception_condition = 70007 in ids and 70005 in ids and 70006 in ids and len(ids) == 3

    integration = list()

    # Return "this term" and "last term" integration data
    if to_init:
        q, has_volume, has_weight = get_group_by_date_query_set(query_set,
                                                                start_date=start_date,
                                                                end_date=end_date,
                                                                specific_year=True)
        q_last, has_volume_last, has_weight_last = get_group_by_date_query_set(query_set,
                                                                               start_date=last_start_date,
                                                                               end_date=last_end_date,
                                                                               specific_year=True)

        if q.count() > 0:
            data_this = pandas_annotate_init(q, hog_exception_condition)
            data_this['name'] = _('This Term')
            data_this['points'] = spark_point_maker(q)
            data_this['base'] = True

            integration.append(data_this)

        if q_last.count() > 0:
            data_last = pandas_annotate_init(q_last, hog_exception_condition)
            data_last['name'] = _('Last Term')
            data_last['points'] = spark_point_maker(q_last)
            data_last['base'] = False

            integration.append(data_last)

    # Return each year integration exclude current term
    else:
        this_year = start_date.year
        query_set = query_set.filter(date__year__lt=this_year)
        # Group by year
        q, has_volume, has_weight = get_group_by_date_query_set(query_set,
                                                                start_date=start_date,
                                                                end_date=end_date,
                                                                specific_year=False)

        if q.count() > 0:
            data_all = pandas_annotate_year(q, hog_exception_condition)
            for dic in data_all:
                year = dic['year']
                q_filter_by_year = q.filter(year=year).order_by('date')
                dic['name'] = '%0.0f' % year
                dic['points'] = spark_point_maker(q_filter_by_year)
                dic['base'] = False

            integration = list(data_all)
            integration.reverse()

    response_data = {
        'type': TypeSerializer(_type).data,
        'integration': integration,
        'has_volume': False,
        'has_weight': False,
        'no_data': len(integration) == 0,
    }

    if integration:
        response_data['has_volume'] = 'sum_volume' in integration[0]
        response_data['has_weight'] = 'avg_avg_weight' in integration[0]

    return response_data


class Day(Func):
    function = 'EXTRACT'
    template = '%(function)s(DAY from %(expressions)s)'
    output_field = IntegerField()


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = IntegerField()


class Year(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR from %(expressions)s)'
    output_field = IntegerField()


class RawAnnotation(RawSQL):
    """
    RawSQL also aggregates the SQL to the `group by` clause which defeats the purpose of adding it to an Annotation.
    See: https://medium.com/squad-engineering/hack-django-orm-to-calculate-median-and-percentiles-or-make-annotations-great-again-23d24c62a7d0
    """
    def get_group_by_cols(self):
        return []


# transfer datetime to unix to_unix format
def to_unix(date):
    return int(time.mktime(date.timetuple()) * 1000)


def to_date(number):
    return datetime.datetime.fromtimestamp(float(number) / 1000.0)

























