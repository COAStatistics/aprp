import datetime
from django.utils import timezone
import logging
from dailytrans.models import DailyTran
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
        if sep is '':
            if roc_format:
                if len(string) < 7:
                    raise OverflowError
                year = string[0:3]
                month = string[3:5]
                day = string[5:7]
            else:
                if len(string) < 8:
                    raise OverflowError
                year = string[0:4]
                month = string[4:6]
                day = string[6:8]
        else:
            year, month, day = string.split(sep)
        try:
            year = int(year)
            month = int(month)
            day = int(day)
        except TypeError:
            raise TypeError
        if roc_format:
            year += 1911
        return datetime.date(year=year, month=month, day=day)

    if date:
        year = date.year
        month = date.month
        day = date.day

        if roc_format:
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


def product_generator(model):
    for obj in model.objects.all():
        if obj.track_item:
            if obj.type is not None:
                yield obj
            if obj.type is None:
                db_logger.warning('Abstract %s Item Is Track Item(track_item=True) But Not Specify Type' % obj.name)


def director(func):

    def interface(start_date=None, end_date=None, format=None, delta=None):
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
            kwargs = func(start_date, end_date)
            end_time = timezone.now()
            duration = end_time - start_time

            if kwargs:
                # update not_updated count
                qs = DailyTran.objects.filter(product__config__code=kwargs['config_code'],
                                              date__range=[start_date, end_date])

                if 'type_id' in kwargs and kwargs['type_id']:
                    qs = qs.filter(product__type__id=kwargs['type_id'])

                for d in qs.filter(update_time__lte=start_time):
                    d.not_updated += 1
                    d.save(update_fields=["not_updated"])
                    db_logger.warning('Daily tran data not update, counted to field "not_updated": %s', str(d), extra={
                        'logger_type': kwargs['logger_type_code'],
                    })

                qs.filter(update_time__gt=start_time).update(not_updated=0)

            return DirectResult(start_date, end_date, duration=duration, success=True)

        except Exception as e:
            logging.exception('msg')
            db_logger.exception(e)
            return DirectResult(start_date, end_date, success=False, msg=e)

    return interface


class DirectResult(object):
    def __init__(self, start_date, end_date, duration=None, success=False, msg=None):
        if not isinstance(start_date, datetime.date):
            raise NotImplementedError
        if not isinstance(end_date, datetime.date):
            raise NotImplementedError
        if not isinstance(success, bool):
            raise NotImplementedError
        self.start_date = start_date
        self.end_date = end_date
        self.success = success
        self.duration = duration
        self.msg = msg

