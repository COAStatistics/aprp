import datetime
import logging
from functools import wraps
from collections import namedtuple
from django.utils import timezone
from apps.dailytrans.models import DailyTran
db_logger = logging.getLogger('aprp')


def date_transfer(sep=None, string=None, date=None, roc_format=False, zfill=None):
    if sep is None:
        raise NotImplementedError
    if string and date:
        raise NotImplementedError
    if date:
        if zfill is None or not isinstance(date, datetime.date):
            raise NotImplementedError
    if string:
        if sep == '':

            # if roc_format:
            #     if len(string) < 7:
            #         raise OverflowError
            #     year = string[0:3]
            #     month = string[3:5]
            #     day = string[5:7]
            # else:
            #     if len(string) < 8:
            #         raise OverflowError
            #     year = string[0:4]
            #     month = string[4:6]
            #     day = string[6:8]

            # 年份長度判斷是否為西元年
            if len(string) == 6:
                year = string[0:2]
                month = string[2:4]
                day = string[4:6]
            elif len(string) == 7:
                year = string[0:3]
                month = string[3:5]
                day = string[5:7]
            elif len(string) == 8:
                year = string[0:4]
                month = string[4:6]
                day = string[6:8]
            else:
                raise OverflowError
        else:
            year, month, day = string.split(sep)
        try:
            year = int(year)
            month = int(month)
            day = int(day)
        except TypeError:
            raise TypeError

        # if roc_format:
        #     year += 1911
        if len(str(year)) <= 3:
            year = date.year + 1911

        return datetime.date(year=year, month=month, day=day)

    if date:
        year = date.year
        month = date.month
        day = date.day

        # if roc_format:
        #     year = date.year - 1911
        if len(str(year)) == 4:
            year = date.year - 1911

        if year < 0:
            raise OverflowError

        year = str(year)
        month = str(month)
        day = str(day)

        if zfill:
            month = month.zfill(2)
            day = day.zfill(2)

        return sep.join((year, month, day))


def date_delta(delta):
    if not isinstance(delta, int):
        raise TypeError
    today = datetime.date.today()
    another_day = today + datetime.timedelta(delta)

    if today > another_day:
        return another_day, today
    else:
        return today, another_day


def date_generator(start_date, end_date, date_range=None):
    if not isinstance(start_date, datetime.date):
        raise NotImplementedError
    if not isinstance(end_date, datetime.date):
        raise NotImplementedError
    if start_date > end_date:
        raise NotImplementedError
    if not date_range:
        raise NotImplementedError

    lock = False
    delta_start_date = start_date
    while not lock:
        delta_end_date = delta_start_date + datetime.timedelta(date_range)

        if delta_end_date > end_date:
            delta_end_date = end_date
            lock = True

        yield delta_start_date, delta_end_date

        delta_start_date = delta_start_date + datetime.timedelta(date_range)


def product_generator(model, type=None, code=None, name=None, **kwargs):
    qs = model.objects.all()
    if type:
        qs = qs.filter(type__id=type)
    if code:
        qs = qs.filter(code=code)
    if name:
        qs = qs.filter(name=name)
    for obj in qs:
        if obj.track_item:
            if obj.type is not None:
                yield obj
            if obj.type is None:
                db_logger.warning('Abstract %s Item Is Track Item(track_item=True) But Not Specify Type' % obj.name)


DirectResult = namedtuple('DirectResult', ('start_date', 'end_date', 'duration', 'success', 'msg'))
DirectResult.__new__.__defaults__ = (None, False, '',)

DirectData = namedtuple('DirectData', ('config_code', 'type_id', 'logger_type_code'))


def director(func):

    @wraps(func)
    def interface(start_date=None, end_date=None, format=None, delta=None, **kwargs):

        code = kwargs.get('code')
        name = kwargs.get('name')

        if start_date and not end_date:
            raise NotImplementedError
        if end_date and not start_date:
            raise NotImplementedError
        if start_date and end_date:
            ii = isinstance
            d = datetime.date
            if ii(start_date, d) and not ii(end_date, d):
                raise NotImplementedError
            if ii(end_date, d) and not ii(start_date, d):
                raise NotImplementedError
            if delta:
                raise NotImplementedError
            if ii(start_date, d) and ii(end_date, d):
                if format:
                    raise NotImplementedError
            if not ii(start_date, d) and not ii(end_date, d):
                if not format:
                    raise NotImplementedError
                start_date = datetime.datetime.strptime(start_date, format)
                end_date = datetime.datetime.strptime(end_date, format)

        else:
            if not delta:
                NotImplementedError
            start_date, end_date = date_delta(delta)

        try:
            start_time = timezone.now()
            data = func(start_date, end_date, **kwargs)
            end_time = timezone.now()
            duration = end_time - start_time

            if isinstance(data, DirectData):
                # update not_updated count
                qs = DailyTran.objects.filter(product__config__code=data.config_code,
                                              date__range=[start_date, end_date])

                if code:
                    qs = qs.filter(product__parent__code=code)

                if name:
                    qs = qs.filter(product__parent__name=name)

                if data.type_id:
                    qs = qs.filter(product__type__id=data.type_id)

                for d in qs.filter(update_time__lte=start_time):
                    if name is None and code is None and kwargs.get('history') is None:
                        d.not_updated += 1
                        d.save(update_fields=["not_updated"])
                        db_logger.warning('Daily tran data not update, counted to field "not_updated": %s', str(d), extra={
                            'logger_type': data.logger_type_code,
                        })
                    else:
                        d.delete()
                        db_logger.warning('Daily tran data has been deleted: {}'.format(str(d)), extra={
                            'logger_type': data.logger_type_code,
                        })

                qs.filter(update_time__gt=start_time).update(not_updated=0)

            return DirectResult(start_date, end_date, duration=duration, success=True)

        except Exception as e:
            logging.exception('msg')
            db_logger.exception(e)
            return DirectResult(start_date, end_date, success=False, msg=e)

    return interface
