import time
import operator
import datetime
from django.db.models.expressions import RawSQL

import numpy as np
import pandas as pd
from pandas import DataFrame
from collections import OrderedDict
from functools import reduce

from django.utils.translation import ugettext as _
from django.db.models import Sum, Avg, F, Func, IntegerField, Value, Q, Case, When, FloatField

from apps.dailytrans.models import DailyTran
from apps.configs.api.serializers import TypeSerializer
from apps.watchlists.models import WatchlistItem
from apps.configs.models import AbstractProduct


def get_query_set(_type, items, sources=None):
    """
    Returns a QuerySet of DailyTran objects filtered by type and product/watchlist item.

    Args:
        _type (Type): The type of the product.
        items (Iterable[WatchlistItem or AbstractProduct]): The items to filter by.
        sources (Iterable[Source], optional): The sources to filter by. Defaults to None.

    Returns:
        QuerySet: A QuerySet of DailyTran objects filtered by type and product/watchlist item.
    """
    # If no items are provided, return an empty QuerySet
    if not items:
        return DailyTran.objects.none()

    # Extract product_ids from WatchlistItem objects and AbstractProduct objects
    product_ids = {item.product_id for item in items if isinstance(item, WatchlistItem)}
    product_ids.update({item.id for item in items if isinstance(item, AbstractProduct)})

    # Extract source_ids from Source objects if sources are provided
    source_ids = set(source.id for source in sources) if sources else None

    # Create the initial queryset filtered by type and product_ids
    query = DailyTran.objects.filter(product__type=_type, product_id__in=product_ids)

    # Filter the queryset by source_ids if sources are provided
    if source_ids:
        query = query.filter(source_id__in=source_ids)

    return query


def get_group_by_date_query_set(query_set, start_date=None, end_date=None, specific_year=True):
    """
    Filters a queryset by date range and calculates aggregated data.
    Args:
        query_set (QuerySet): The queryset to filter and aggregate.
        start_date (datetime.date, optional): The start date of the date range. Defaults to None.
        end_date (datetime.date, optional): The end date of the date range. Defaults to None.
        specific_year (bool, optional): Whether to filter by specific year or exclude year. Defaults to True.
    Returns:
        tuple: A tuple containing the aggregated dataframe, a boolean indicating if volume data is present,
               and a boolean indicating if weight data is present.
    """

    # Check if the queryset is empty
    if not query_set:
        return pd.DataFrame(columns=['date', 'avg_price', 'num_of_source']), False, False

    # Check if volume and weight data is present in the queryset
    has_volume = query_set.filter(volume__isnull=False).count() > (0.8 * query_set.count())
    has_weight = query_set.filter(avg_weight__isnull=False).count() > (0.8 * query_set.count())

    # Filter the queryset by date range if start_date and end_date are provided
    if isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date):
        if specific_year:
            query_set = query_set.filter(date__range=[start_date, end_date])
        else:
            query_set = query_set.between_month_day_filter(start_date, end_date)

    # Filter the queryset by volume and weight if both are present
    if has_volume and has_weight:
        query_set = query_set.filter(Q(volume__gt=0) & Q(avg_weight__gt=0))

    # Convert the queryset to a dataframe and select relevant columns
    df = pd.DataFrame(list(query_set.values()))
    df = df[['product_id', 'source_id', 'date', 'avg_price', 'avg_weight', 'volume']]
    df.fillna(1, inplace=True)

    # Calculate total price and weight
    df['total_price'] = df['avg_price'] * df['avg_weight'] * df['volume']
    df['total_weight'] = df['avg_weight'] * df['volume']

    # Calculate number of sources
    df['num_of_source'] = 1

    # Group the dataframe by date and product_id and calculate aggregated values
    group = df.groupby(['date', 'product_id'])
    df_fin = group.sum()
    df_fin['avg_price'] = df_fin['total_price'] / df_fin['total_weight']
    df_fin['avg_avg_weight'] = df_fin['total_weight'] / df_fin['volume']
    df_fin['avg_volume'] = df_fin['volume'] / df_fin['num_of_source']
    df_fin.reset_index(inplace=True)
    df_fin = df_fin.sort_values('date')

    return df_fin[
        ['date', 'avg_price', 'num_of_source', 'volume', 'avg_volume', 'avg_avg_weight']], has_volume, has_weight


def get_daily_price_volume(_type, items, sources=None, start_date=None, end_date=None):
    """
    Get daily price and volume data.
    Args:
        _type (str): The type of data.
        items (list): The list of items.
        sources (list, optional): The list of sources. Defaults to None.
        start_date (str, optional): The start date. Defaults to None.
        end_date (str, optional): The end date. Defaults to None.
    Returns:
        dict: The response data containing the type, highchart data, raw data, and no_data flag.
    """
    query_set = get_query_set(_type, items, sources)
    q, has_volume, has_weight = get_group_by_date_query_set(query_set, start_date, end_date)

    if q.size == 0: return {'no_data': True}

    columns = [
        {'value': _('Date'), 'format': 'date'},
        {'value': _('Average Price'), 'format': 'avg_price'}
    ]

    if has_volume:
        columns.append({'value': _('Sum Volume'), 'format': 'volume'})
    if has_weight:
        columns.append({'value': _('Average Weight'), 'format': 'avg_avg_weight'})

    raw_data = {'columns': columns, 'rows': [[dic['date'], dic['avg_price']] for _, dic in q.iterrows()]}

    start_date = start_date or q['date'].iloc[0]
    end_date = end_date or q['date'].iloc[-1]
    diff = (end_date - start_date).days + 1
    date_list = pd.date_range(start_date, periods=diff, freq='D')

    missing_point_data = q.set_index('date').reindex(date_list, method='ffill')

    highchart_data = {'avg_price': [[to_unix(date), price] for date, price in missing_point_data['avg_price'].items()]}

    if has_volume:
        raw_data['rows'] = [[dic['date'], dic['avg_price'], dic['volume']] for _, dic in q.iterrows()]
        highchart_data['sum_volume'] = [[to_unix(date), volume] for date, volume in missing_point_data['volume'].items()]
    if has_weight:
        raw_data['rows'] = [[dic['date'], dic['avg_price'], dic['volume'], dic['avg_avg_weight']] for _, dic in q.iterrows()]
        highchart_data['avg_weight'] = [[to_unix(date), weight] for date, weight in missing_point_data['avg_avg_weight'].items()]

    response_data = {
        'type': TypeSerializer(_type).data,
        'highchart': highchart_data,
        'raw': raw_data,
        'no_data': len(highchart_data['avg_price']) == 0,
    }

    return response_data


def get_daily_price_by_year(_type, items, sources=None):
    """
    Get the daily price data by year for a given type and items.

    Args:
        _type (Type): The type of the product.
        items (Iterable[WatchlistItem or AbstractProduct]): The items to filter by.
        sources (Iterable[Source], optional): The sources to filter by. Defaults to None.

    Returns:
        dict: The response data containing highchart data and raw data.
    """
    def get_result(key):
        """
        Generate the result dictionary for a given key.
        Args:
            key (str): The key to access the data in the result dictionary.
        Returns:
            dict: The result dictionary containing the highchart data and raw data.
        """
        result = {year: [] for year in pd.to_datetime(q['date']).dt.year.unique()}
        if q.size == 0:
            return {
                'highchart': result,
                'raw': None
            }

        date_list = pd.date_range(datetime.date(2016, 1, 1), datetime.date(2016, 12, 31), freq='D')
        for i, dic in q.iterrows():
            date = datetime.date(year=2016, month=dic['date'].month, day=dic['date'].day)
            result[dic['date'].year].append((to_unix(date), dic[key]) if dic[key] else None)

            if not ((dic['date'].year % 4 == 0 and dic['date'].year % 100 != 0) or dic['date'].year % 400 == 0) and dic[
                'date'].month == 2 and dic['date'].day == 28:
                result[dic['date'].year].append((to_unix(datetime.date(2016, 2, 29)), None))

        df = pd.DataFrame.from_dict(result, orient='columns')
        df = df.applymap(lambda x: x[1] if isinstance(x, tuple) else x)
        df.insert(0, 'date', date_list)
        row_empty = df.iloc[:, 1:].isna().all(axis=1)
        raw_data_rows_remove_empty = df[~row_empty]
        raw_data_rows_remove_empty.fillna('', inplace=True)
        raw_data_rows_remove_empty = raw_data_rows_remove_empty.values.tolist()

        raw_data_columns = [{'value': _('Date'), 'format': 'date'}]
        raw_data_columns.extend([{'value': str(year), 'format': key} for year in years])

        raw_data = {
            'columns': raw_data_columns,
            'rows': raw_data_rows_remove_empty
        }

        return {
            'highchart': result,
            'raw': raw_data,
        }

    query_set = get_query_set(_type, items, sources)
    q, has_volume, has_weight = get_group_by_date_query_set(query_set)
    if q.size == 0:
        return {
            'no_date': True
        }

    years = set([date.year for date in q['date']])

    def selected_year(y):
        this_year = datetime.date.today().year
        return this_year > y >= datetime.date.today().year - 5

    q = q.set_index('date').reindex(
        pd.date_range(datetime.date(q['date'].min().year, 1, 1), datetime.date(q['date'].max().year, 12, 31)),
        fill_value=None)
    q = q.reset_index().rename(columns={'index': 'date'})

    response_data = {
        'years':[(year, selected_year(year)) for year in years],
        'type': TypeSerializer(_type).data,
        'price': get_result('avg_price'),
    }

    if has_volume:
        response_data['volume'] = get_result('volume')

    if has_weight:
        response_data['weight'] = get_result('avg_avg_weight')

    response_data['no_data'] = len(response_data['price']['highchart'].keys()) == 0

    return response_data


def annotate_avg_price(df, key):
    """
    Calculate the monthly average price for each group in the DataFrame.
    Args:
        df (pd.DataFrame): The input DataFrame.
        key (str): The column name to group by.
    Returns:
        pd.DataFrame: The DataFrame with the monthly average price added.
    """
    df['weighted_avg_price'] = df['avg_price'] * df['volume'] * df['avg_avg_weight'] * df['num_of_source']
    df['weighted_sum_volume_weight'] = df['volume'] * df['avg_avg_weight'] * df['num_of_source']
    df['weighted_avg_price'] = df.groupby(key)['weighted_avg_price'].transform('sum')
    df['weighted_sum_volume_weight'] = df.groupby(key)['weighted_sum_volume_weight'].transform('sum')
    df['monthly_avg_price'] = df['weighted_avg_price'] / df['weighted_sum_volume_weight']
    return df.groupby(key)['monthly_avg_price'].first()


def annotate_avg_weight(df, key):
    """
    Calculate the average weight for each group in the DataFrame.
    Args:
        df (pd.DataFrame): The input DataFrame.
        key (str): The column name to group by.
    Returns:
        pd.DataFrame: The DataFrame with the average weight added.
    """
    df['weighted_avg_weight'] = df['sum_volume'] * df['avg_avg_weight']
    df['weighted_sum_volume'] = df['sum_volume']
    df['weighted_avg_weight'] = df.groupby(key)['weighted_avg_weight'].transform('sum')
    df['weighted_sum_volume'] = df.groupby(key)['weighted_sum_volume'].transform('sum')
    df['avg_weight'] = df['weighted_avg_weight'] / df['weighted_sum_volume']
    return df.groupby(key)['avg_weight'].first()


def get_monthly_price_distribution(_type, items, sources=None, selected_years=None):
    """
    Calculates the monthly price distribution for a given type and items.
    Args:
        _type (str): The type of data to calculate the distribution for.
        items (List[str]): The items to calculate the distribution for.
        sources (List[str], optional): The sources of the data. Defaults to None.
        selected_years (List[int], optional): The years to calculate the distribution for. Defaults to None.
    Returns:
        Dict: A dictionary containing the distribution data for each year and type.
            - 'type' (str): The type of data calculated.
            - 'years' (List[int]): The years the distribution is calculated for.
            - 'price' (Dict): The distribution data for the 'avg_price' key.
            - 'volume' (Dict, optional): The distribution data for the 'sum_volume' key if available.
            - 'weight' (Dict, optional): The distribution data for the 'avg_avg_weight' key if available.
            - 'no_data' (bool): True if no data is available for the distribution, False otherwise.
    """
    def get_result(key):
        """
        Generates the result for a given key.
        Args:
            key (str): The key to generate the result for.
        Returns:
            dict: A dictionary containing the 'highchart' and 'raw' data.
                - 'highchart' (dict): A dictionary containing the data for highchart plotting.
                    - 'perc_0' (list): A list of tuples representing the percentile 0 values.
                    - 'perc_25' (list): A list of tuples representing the percentile 25 values.
                    - 'perc_50' (list): A list of tuples representing the percentile 50 values.
                    - 'perc_75' (list): A list of tuples representing the percentile 75 values.
                    - 'perc_100' (list): A list of tuples representing the percentile 100 values.
                    - 'mean' (list): A list of tuples representing the mean values.
                    - 'years' (list): A list of years.
                - 'raw' (dict): A dictionary containing the raw data.
                    - 'columns' (list): A list of dictionaries representing the columns.
                        - 'value' (str): The value of the column.
                        - 'format' (str): The format of the column.
                    - 'rows' (list): A list of lists representing the rows.
                        - Each inner list contains the values for each column in the same order as 'columns'.
        Note:
            - The function assumes that the 'q' variable is defined and contains the necessary data.
            - The 'years' variable is not defined in the provided code snippet.
        """
        highchart_data = {}
        raw_data = {}

        if q.empty :
            return {
                'highchart': highchart_data,
                'raw': raw_data,
            }
        s_quantile = q.groupby('month')[key].quantile([.0, .25, .5, .75, 1])
        if key == 'avg_price':
            s_mean = annotate_avg_price(q, 'month')
        elif key == 'avg_avg_weight':
            s_mean = annotate_avg_weight(q, 'month')
        else:
            s_mean = q.groupby('month')[key].mean()

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
            'rows': [[i, s_quantile.loc[i][0.0], s_quantile.loc[i][0.25], s_quantile.loc[i][0.5], s_quantile.loc[i][0.75], s_quantile.loc[i][1],
                      s_mean.loc[i]] for i in s_quantile.index.levels[0]]
        }

        return {
            'highchart': highchart_data,
            'raw': raw_data,
        }

    query_set = get_query_set(_type, items, sources)

    if selected_years:
        query_set = query_set.filter(date__year__in=selected_years)

    q, has_volume, has_weight = get_group_by_date_query_set(query_set)
    q['month'] = pd.to_datetime(q['date']).dt.month

    years = list(pd.to_datetime(q['date']).dt.year.unique())

    response_data = {
        'type': TypeSerializer(_type).data,
        'years': years,
        'price': get_result('avg_price')
    }

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

    def pandas_annotate_init(df):
        series = df.mean()
        result = series.T.to_dict()

        # group by all rows by added column 'key'
        df['key'] = 'value'
        price = annotate_avg_price(df, 'key')  # return {'value': price}
        # apply annotated price to result avg_price
        result['avg_price'] = price['value']

        return result

    def pandas_annotate_year(qs, has_volume, has_weight, start_date=None, end_date=None):
        df = qs.copy()
        if start_date and end_date and start_date.year != end_date.year:
            df_list = []
            df['avg_price'] = df['avg_price'] * df['sum_volume'] * df['avg_avg_weight'] * df['num_of_source']
            df['sum_volume_weight'] = df['sum_volume'] * df['avg_avg_weight'] * df['num_of_source']
            for i in range(1, start_date.year - q.first()['year'] + 1):
                splitted_df = df[
                    (df['date'] >= datetime.date(start_date.year - i, start_date.month, start_date.day)) \
                    & (df['date'] <= datetime.date(end_date.year - i, end_date.month, end_date.day)) \
                    ].mean()
                splitted_df['year'] = start_date.year - i
                splitted_df['end_year'] = end_date.year - i
                df_list.append(splitted_df)
            df = pd.concat(df_list, axis=1).T
            df['avg_price'] = df['avg_price'] / df['sum_volume_weight']
        else:
            df['avg_price'] = df['avg_price'] * df['sum_volume'] * df['avg_avg_weight'] * df['num_of_source']
            df['sum_volume_weight'] = df['sum_volume'] * df['avg_avg_weight'] * df['num_of_source']
            df = df.groupby(['year'], as_index=False).mean()
            df['avg_price'] = df['avg_price'] / df['sum_volume_weight']

        result = df.T.to_dict().values()
        # group by year
        price = annotate_avg_price(df, 'year')  # return {2017: price1, 2018: price2}
        # apply annotated price to result avg_price
        for dic in result:
            year = dic['year']
            if year in price:
                dic['avg_price'] = price[year]

        return result

    query_set = get_query_set(_type, items, sources)

    diff = end_date - start_date + datetime.timedelta(1)

    last_start_date = start_date - diff
    last_end_date = end_date - diff

    integration = []

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

        q_fy = query_set.filter(date__gte=datetime.datetime(start_date.year - 5, start_date.month, start_date.day), \
                                date__lte=datetime.datetime(end_date.year - 1, end_date.month, end_date.day))
        q_fy, has_volume_fy, has_weight_fy = get_group_by_date_query_set(q_fy,
                                                                         start_date=start_date,
                                                                         end_date=end_date,
                                                                         specific_year=False)

        if q.count() > 0:
            data_this = pandas_annotate_init(q)
            data_this['name'] = _('This Term')
            data_this['points'] = spark_point_maker(q)
            data_this['base'] = True
            data_this['order'] = 1
            integration.append(data_this)

        if q_last.count() > 0:
            data_last = pandas_annotate_init(q_last)
            data_last['name'] = _('Last Term')
            data_last['points'] = spark_point_maker(q_last)
            data_last['base'] = False
            data_last['order'] = 2
            integration.append(data_last)

        if start_date.year - q_fy.order_by('date').first()['year'] == 5:
            data_fy = pandas_annotate_init(q_fy)
            data_fy['name'] = _('5 Years')
            data_fy['points'] = spark_point_maker(q_fy)
            data_fy['base'] = False
            data_fy['order'] = 3
            integration.append(data_fy)

    # Return each year integration exclude current term
    else:
        this_year = end_date.year
        query_set = query_set.filter(date__year__lt=this_year)
        # Group by year
        q, has_volume, has_weight = get_group_by_date_query_set(query_set,
                                                                start_date=start_date,
                                                                end_date=end_date,
                                                                specific_year=False)

        if q.count() > 0 and start_date.year == end_date.year:
            data_all = pandas_annotate_year(q, has_volume, has_weight)
            for dic in data_all:
                year = dic['year']
                q_filter_by_year = q.filter(year=year).order_by('date')
                dic['name'] = '%0.0f' % year
                dic['points'] = spark_point_maker(q_filter_by_year)
                dic['base'] = False
                dic['order'] = 4 + this_year - year

            integration = list(data_all)
            integration.reverse()

        elif q.count() > 0 and start_date.year != end_date.year:
            data_all = pandas_annotate_year(q, has_volume, has_weight, start_date, end_date)
            for dic in data_all:
                start_year = int(dic['year'])
                end_year = int(dic['end_year'])
                q_filter_by_year = q.filter(date__gte=datetime.date(start_year, start_date.month, start_date.day), \
                                            date__lte=datetime.date(end_year, end_date.month, end_date.day))
                dic['name'] = '{}~{}'.format(start_year, end_year)
                dic['points'] = spark_point_maker(q_filter_by_year)
                dic['base'] = False
                dic['order'] = 4 + this_year - start_year

            integration = list(data_all)
            integration.reverse()

    response_data = {
        'type': TypeSerializer(_type).data,
        'integration': integration,
        'has_volume': False,
        'has_weight': False,
        'no_data': not integration,
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
