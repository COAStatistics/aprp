import datetime
import calendar
import openpyxl

from openpyxl.styles import PatternFill
from pathlib import Path
from django.conf import settings

from apps.watchlists.models import Watchlist, WatchlistItem, MonitorProfile
from apps.dailytrans.models import DailyTran
from apps.dailytrans.utils import get_group_by_date_query_set
from apps.fruits.models import Fruit
from apps.configs.models import Source


TEMPLATE = str(settings.BASE_DIR('apps/dailytrans/reports/template.xlsx'))

SHEET_FILL = PatternFill(
    start_color='f2dcdb',
    end_color='f2dcdb',
    fill_type='solid',
)

WEEKDAY = {
    0: '週一',
    1: '週二',
    2: '週三',
    3: '週四',
    4: '週五',
    5: '週六',
    6: '週日',
}

SHEET_FORMAT = {
    'F': '#,##0.0_);[Red]\\(#,##0.0\\)',
    'G': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'H': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'L': '0.0_ ',
    'M': '#,##0.0_ ',
    'N': '#,##0.0_ ',
    'O': '#,##0.0_ ',
    'P': '#,##0.0_ ',
    'Q': '#,##0.0_ ',
    'R': '#,##0.0_ ',
    'S': '#,##0.0_ ',
    'T': '#,##0_ ',
    'U': '#,##0.0_ ',
    'W': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'X': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'Y': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'Z': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'AA': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'AB': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'AC': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
    'AD': '_-* #,##0.0_-;\\-* #,##0.0_-;_-* "-"?_-;_-@_-',
}


def get_avg_price(qs, has_volume, week_start=None, week_end=None):
    total_price = list()
    total_volume = list()
    if has_volume:
        for q in qs:
            if week_start is not None and week_end is not None:
                if week_start.date() <= q['date'] <= week_end.date():
                    total_price.append(q['avg_price'] * q['sum_volume'])
                    total_volume.append(q['sum_volume'])
            else:
                total_price.append(q['avg_price'] * q['sum_volume'])
                total_volume.append(q['sum_volume'])
        return sum(total_price) / sum(total_volume) if len(total_volume) else 0
    else:
        for q in qs:
            if week_start is not None and week_end is not None:
                if week_start.date() <= q['date'] <= week_end.date():
                    total_price.append(q['avg_price'])
            else:
                total_price.append(q['avg_price'])
    return sum(total_price) / len(total_price) if len(total_price) else 0


def get_avg_volume(qs, week_start=None, week_end=None):
    total_volume = list()
    for q in qs:
        if week_start.date() <= q['date'] <= week_end.date():
            total_volume.append(q['sum_volume'])
    return sum(total_volume) / len(total_volume) if len(total_volume) else 0


class DailyReportFactory(object):
    def __init__(self, specify_day):
        self.specify_day = specify_day
        self.this_week_start = self.specify_day - datetime.timedelta(6)
        self.this_week_end = self.specify_day
        self.last_week_start = self.this_week_start - datetime.timedelta(7)
        self.last_week_end = self.this_week_start - datetime.timedelta(1)
        self.last_year_month_start = datetime.datetime(self.specify_day.year - 1, self.specify_day.month, 1)
        self.last_year_month_end = datetime.datetime(self.specify_day.year - 1,
                                                     self.specify_day.month,
                                                     calendar.monthrange(self.specify_day.year - 1,
                                                                         self.specify_day.month)[1])

        self.row_visible = list()
        self.row_marked = list()
        self.result = dict()
        self.col_dict = dict()
        self.generate_list_dict()

    def generate_list_dict(self):
        for i in range(0, 7):
            date = self.this_week_start.date() + datetime.timedelta(i)
            self.col_dict['{}'.format(date)] = '{}'.format(chr(77 + i))
            if i < 3:
                self.col_dict['{}_volume'.format(date)] = '{}'.format(chr(88 + i))
            else:
                self.col_dict['{}_volume'.format(date)] = 'A{}'.format(chr(65 + i - 3))

    def check_months(self, item):
        if not item.months.filter(name__icontains=self.specify_day.month):
            self.row_marked.append(item.row)

    def input_sheet_date(self, sheet, index):
        month = (self.this_week_start + datetime.timedelta(index)).month
        day = (self.this_week_start + datetime.timedelta(index)).day
        sym = chr(77 + index)
        sheet['{}8'.format(sym)] = '{}月\n{}日'.format(month, day)
        if index >= 3:
            sym = 'A{}'.format(chr(65 + index - 3))
        else:
            sym = chr(88 + index)
        sheet['{}8'.format(sym)] = '{}月\n{}日'.format(month, day)
        return sheet

    def get_data(self, query_set, product, row, monitor_price):
        qs, has_volume, has_weight = get_group_by_date_query_set(query_set, self.last_week_start, self.this_week_end)
        self.result[product] = dict()
        for q in qs:
            if q['date'] >= self.this_week_start.date():
                self.result[product].update({
                    '{}{}'.format(self.col_dict['{}'.format(q['date'])], row): q['avg_price'],
                })
            if has_volume and q['date'] >= self.this_week_start.date():
                self.result[product].update({
                    '{}{}'.format(self.col_dict['{}_volume'.format(q['date'])], row): q['sum_volume'],
                })
        last_avg_price = get_avg_price(qs, has_volume, self.last_week_start, self.last_week_end)
        this_avg_price = get_avg_price(qs, has_volume, self.this_week_start, self.this_week_end)
        if last_avg_price > 0:
            self.result[product].update({
                'L{}'.format(row): ((this_avg_price - last_avg_price) / last_avg_price * 100),
            })
        if has_volume:
            last_avg_volume = get_avg_volume(qs, self.last_week_start, self.last_week_end)
            this_avg_volume = get_avg_volume(qs, self.this_week_start, self.this_week_end)
            self.result[product].update({
                'T{}'.format(row): this_avg_volume,
            })
            if last_avg_volume > 0:
                self.result[product].update({
                    'U{}'.format(row): ((this_avg_volume - last_avg_volume) / last_avg_volume * 100),
                })
        if monitor_price:
            self.result[product].update({
                'F{}'.format(row): monitor_price,
            })
        self.result[product].update({
            'H{}'.format(row): this_avg_price,
            'W{}'.format(row): last_avg_price,
        })

    def update_data(self, query_set, product, row):
        qs, has_volume, has_weight = get_group_by_date_query_set(query_set,
                                                                 self.last_year_month_start,
                                                                 self.last_year_month_end)
        last_year_avg_price = get_avg_price(qs, has_volume)
        if last_year_avg_price > 0:
            self.result[product].update({
                'G{}'.format(row): last_year_avg_price,
            })

    def update_rams(self, item, row):
        query_set = DailyTran.objects.filter(product__in=item.product_list(), source__in=item.sources())
        for i in range(0, 7):
            week_day = self.this_week_start + datetime.timedelta(i)
            qs = query_set.filter(date__lte=week_day.date()).order_by('-date')
            if qs:
                qs = qs.first()
            else:
                continue
            if i == 0 or qs.date == week_day.date():
                self.result[item.product.name].update({
                    '{}{}'.format(self.col_dict['{}'.format(week_day.date())], row): qs.avg_price,
                })
            else:
                self.result[item.product.name].update({
                    '{}{}'.format(self.col_dict['{}'.format(week_day.date())], row): qs.date.strftime('(%m/%d)'),
                })

    def update_cattles(self, item, row):
        query_set = DailyTran.objects.filter(product__in=item.product_list())
        last_week_price = list()
        this_week_price = list()
        for i in range(0, 7):
            week_day = self.this_week_start + datetime.timedelta(i)
            qs = query_set.filter(date__lte=week_day.date()).order_by('-date')
            if qs:
                qs = qs.first()
                this_week_price.append(qs.avg_price)
            else:
                continue
            self.result[item.product.name].update({
                '{}{}'.format(self.col_dict['{}'.format(week_day.date())], row): qs.avg_price,
            })
        for i in range(1, 8):
            week_day = self.this_week_start - datetime.timedelta(i)
            qs = query_set.filter(date__lte=week_day.date()).order_by('-date')
            if qs:
                qs = qs.first()
                last_week_price.append(qs.avg_price)
        if len(last_week_price):
            last_week_avg_price = sum(last_week_price) / len(last_week_price)
            self.result[item.product.name].update({
                'W{}'.format(row): last_week_avg_price,
            })
        if len(this_week_price):
            this_week_avg_price = sum(this_week_price) / len(this_week_price)
            self.result[item.product.name].update({
                'H{}'.format(row): this_week_avg_price,
            })
        if len(last_week_price) and len(this_week_price):
            self.result[item.product.name].update({
                'L{}'.format(row): ((this_week_avg_price - last_week_avg_price) / last_week_avg_price * 100),
            })

    def report(self):
        watchlist = Watchlist.objects.filter(
            start_date__year=self.specify_day.year,
            start_date__month__lte=self.specify_day.month,
            end_date__month__gte=self.specify_day.month
        ).first()
        monitor = MonitorProfile.objects.filter(watchlist=watchlist, row__isnull=False)

        for item in monitor:
            self.row_visible.append(item.row)
            query_set = DailyTran.objects.filter(product__in=item.product_list())
            if item.sources():
                query_set = query_set.filter(source__in=item.sources())
            self.get_data(query_set, item.product.name, item.row, item.price)
            # last year avg_price of month
            query_set = DailyTran.objects.filter(product__in=item.product_list(),
                                                 date__year=self.specify_day.year-1,
                                                 date__month=self.specify_day.month)
            if item.sources():
                query_set = query_set.filter(source__in=item.sources())
            self.update_data(query_set, item.product.name, item.row)
            if '羊' in item.product.name:
                self.update_rams(item, item.row)
            if '牛' in item.product.name:
                self.update_cattles(item, item.row)
            self.check_months(item)

        # 長糯, 稻穀, 全部花卉 L, 火鶴花 FB, 文心蘭 FO3
        extra_product = [(3001, 10), (3002, 9), (3508, 99), (3509, 100), (3510, 103)]
        for item in extra_product:
            self.row_visible.append(item[1])
            watchlist_item = WatchlistItem.objects.filter(id=item[0]).first()
            product = watchlist_item.product
            query_set = DailyTran.objects.filter(product=product)
            if watchlist_item.sources.all():
                query_set = query_set.filter(source__in=watchlist_item.sources.all())
            self.get_data(query_set, product.name, item[1], None)
            # last year avg_price of month
            query_set = DailyTran.objects.filter(product=product,
                                                 date__year=self.specify_day.year-1,
                                                 date__month=self.specify_day.month)
            if watchlist_item.sources.all():
                query_set = query_set.filter(source__in=watchlist_item.sources.all())
            self.update_data(query_set, product.name, item[1])

        # 香蕉台北一二批發
        self.row_visible.append(73)
        product = Fruit.objects.get(id=50063)
        sources = Source.objects.filter(id__in=[20001, 20002])
        query_set = DailyTran.objects.filter(product=product, source__in=sources)
        self.get_data(query_set, '{}{}'.format(product.name, product.type), 73, None)
        query_set = DailyTran.objects.filter(product=product, date__year=self.specify_day.year-1, date__month=self.specify_day.month)
        self.update_data(query_set, '{}{}'.format(product.name, product.type), 73)

    @staticmethod
    def get_sheet_format(key):
        chr1 = key[0]
        chr2 = key[1]
        if 65 <= ord(chr1) <= 90 and 65 <= ord(chr2) <= 90:
            return SHEET_FORMAT.get(chr1 + chr2)
        else:
            return SHEET_FORMAT.get(chr1)

    @staticmethod
    def roc_date_format(date, sep='.'):
        return sep.join([
            str(date.year - 1911),
            str(date.month).zfill(2),
            str(date.day).zfill(2)
        ])

    def get_sheet(self):
        wb = openpyxl.load_workbook(TEMPLATE)
        sheet_name = wb.get_sheet_names()[0]
        sheet = wb.get_sheet_by_name(sheet_name)

        for i in range(0, 7):
            sheet = self.input_sheet_date(sheet, i)
        sheet['G6'] = '{}\n年{}月\n平均價格'.format(self.specify_day.year - 1912, self.specify_day.month)
        last_week_range = '{}/{}~{}/{}'.format(
            self.last_week_start.month, self.last_week_start.day, self.last_week_end.month, self.last_week_end.day
        )
        sheet['W8'] = last_week_range

        for key, value in self.result.items():
            for k, v in value.items():
                try:
                    if v != 0 or v == 0 and 'L' in k or v == 0 and 'U' in k:
                        sheet[k] = v
                    sheet_format = self.get_sheet_format(k)
                    if sheet_format:
                        sheet[k].number_format = sheet_format
                except Exception:
                    pass

        for i in range(9, 132):
            if i not in self.row_visible:
                sheet.row_dimensions[i].hidden = True

        for i in self.row_marked:
            sheet['B{}'.format(i)].fill = SHEET_FILL

        return wb

    def __call__(self, output_dir=settings.BASE_DIR):
        date = self.specify_day + datetime.timedelta(1)
        file_name = '{}-{}價格{}'.format(
            self.roc_date_format(self.this_week_start),
            self.roc_date_format(self.this_week_end),
            WEEKDAY.get(date.weekday()))

        file_path = Path(output_dir, file_name).with_suffix('.xlsx')

        self.report()
        sheet = self.get_sheet()
        sheet.save(file_path)

        return file_name, file_path
