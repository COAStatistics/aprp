import datetime
import calendar
import openpyxl
import pandas as pd

from openpyxl.styles import PatternFill, Font
from pathlib import Path
from django.conf import settings

from apps.watchlists.models import Watchlist, WatchlistItem, MonitorProfile
from apps.dailytrans.models import DailyTran
from apps.dailytrans.utils import get_group_by_date_query_set, Year, Month, Day
from apps.fruits.models import Fruit
from apps.configs.models import Source, AbstractProduct
from apps.flowers.models import Flower
from django.db.models import Q
from django.db.models import Sum, Avg, F, Func, IntegerField

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

# 日報下方資料來源對應品項及其來源說明;香蕉排在本項最後一列加上"一般農產品的資料來源說明",下載日報會出現欄位長度超過列印邊界,移到本項第一列以避免此問題
desc_1 = [
    ('香蕉', '香蕉產地價格(上品-中寮、中埔、旗山、美濃及高樹等農會查報上品價格之簡單平均)、(下品-中寮及中埔農會查報下品價格之簡單平均)'),
    ('落花生', '落花生產地價格(芳苑、虎尾、土庫、北港及元長等農會查報價格之簡單平均)'),
    ('紅豆', '紅豆產地價格(屏東縣萬丹鄉、新園鄉等產地農會查報價格之簡單平均)'),
    ('大蒜', '乾蒜頭產地價格(伸港、虎尾、土庫、元長及四湖等農會查報價格之簡單平均)'),
    ('甘薯', '甘藷產地價格(大城及水林等農會查報價格之簡單平均)'),
    ('桶柑', '桶柑產地價格(峨眉、寶山及和平等農會查報價格之簡單平均)'),
    ('柚子', '文旦柚產地價格(八里、冬山、西湖、斗六、麻豆、下營及瑞穗等農會查報價格之簡單平均)'),
    ('蓮霧', '蓮霧產地價格(六龜、枋寮及南州等農會查報價格之簡單平均)'),
    ('鳳梨', '金鑽鳳梨產地價格(名間、古坑、民雄、關廟、大樹、高樹和內埔等農會查報價格之簡單平均)'),
    ('雜柑', '檸檬產地價格(旗山、九如、里港、鹽埔及高樹等農會查報價格之簡單平均)'),
    ('梅', '竿採梅產地價格(國姓、六龜、甲仙和東河等農會查報價格之簡單平均)'),
    ('鳳梨釋迦', '鳳梨釋迦產地價格(台東地區農會查報價格)')
]

desc_2 = ['新興梨', '豐水梨', '柿子']

desc_3 = [
    '花卉交易(全部花卉市場) 交易量：火鶴花以單枝，文心蘭10枝，香水百合5枝─農產品行情報導，本部農糧署。',
    '95KG至155KG規格毛豬拍賣價格及土番鴨、白肉雞、雞蛋產地價格—中央畜產會。',
    '550KG以上肉牛產地價格—本部畜產試驗所恆春分所及中央畜產會。',
    '努比亞雜交閹公羊拍賣價格—彰化縣肉品拍賣市場。',
    '紅羽土雞產地價格(北區)—中華民國養雞協會。',
    '水產品產地價格─本部漁業署。'
]


def get_avg_price(qs, has_volume, has_weight, week_start=None, week_end=None):
    total_price = []
    total_volume = []
    if has_volume and has_weight:   # 新增有日均重量的品項計算平均價格公式
        total_price = qs['avg_price'] * qs['sum_volume'] * qs['avg_avg_weight']
        total_volume_weight = qs['sum_volume'] * qs['avg_avg_weight']
        return total_price.sum() / total_volume_weight.sum() if len(total_volume_weight) else 0
    elif has_volume:
        total_price = qs['avg_price'] * qs['sum_volume']
        total_volume = qs['sum_volume']
    
        return total_price.sum() / total_volume.sum() if len(total_volume) else 0
    else:
        return qs['avg_price'].mean()


def get_avg_volume(qs, week_start=None, week_end=None):
    return qs['sum_volume'].mean()


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

        self.row_visible = []
        self.row_marked = []
        self.result = {}
        self.col_dict = {}
        self.generate_list_dict()
        self.item_desc = []

    def generate_list_dict(self):
        for i in range(7):
            date = self.this_week_start.date() + datetime.timedelta(i)
            self.col_dict[f'{date}'] = f'{chr(77 + i)}'
            if i < 3:
                self.col_dict[f'{date}_volume'] = f'{chr(88 + i)}'
            else:
                self.col_dict[f'{date}_volume'] = f'A{chr(65 + i - 3)}'

    def check_months(self, item):
        # 不在監控品項月份變更底色改為在顯示月份內的品項顯示        
        # if item.months.filter(name__icontains=self.specify_day.month) or item.always_display:
        #原判斷條件導致10/11/12月份的品項在1/2月分也會出現
        if item.months.filter(name=f'{self.specify_day.month}月') or item.always_display:
            self.row_visible.append(item.row)
            if item.product.name == '梨':
                if self.specify_day.month in [5, 6]:
                    self.item_desc.append('豐水梨')
                elif self.specify_day.month in [7, 8]:
                    self.item_desc.append('新興梨')
            else:
                self.item_desc.append(item.product.name)

    def input_sheet_date(self, sheet, index):
        month = (self.this_week_start + datetime.timedelta(index)).month
        day = (self.this_week_start + datetime.timedelta(index)).day
        sym = chr(77 + index)
        sheet[f'{sym}8'] = f'{month}月\n{day}日'
        sym = f'A{chr(65 + index - 3)}' if index >= 3 else chr(88 + index)
        sheet[f'{sym}8'] = f'{month}月\n{day}日'
        return sheet

    def get_data(self, query_set, product, row, monitor_price):
        qs, has_volume, has_weight = get_group_by_date_query_set(query_set, self.last_week_start, self.this_week_end)
        self.result[product] = {}
        for i, q in qs.iterrows():

            if q['date'] >= self.this_week_start.date():
                self.result[product].update(
                    {f"""{self.col_dict[f"{q['date']}"]}{row}""": q['avg_price']}
                    )
            if has_volume and q['date'] >= self.this_week_start.date():
                self.result[product].update(
                    {f"""{self.col_dict[f"{q['date']}_volume"]}{row}""": q[
                            'sum_volume'
                        ]
                    })
        last_avg_price = get_avg_price(qs[(pd.to_datetime(qs['date']) >= (self.last_week_start)) 
                                          & (pd.to_datetime(qs['date']) <= (self.last_week_end - datetime.timedelta(1)))], has_volume, has_weight)
        this_avg_price = get_avg_price(qs[(pd.to_datetime(qs['date']) >= (self.this_week_start)) 
                                          & (pd.to_datetime(qs['date']) <= (self.this_week_end - datetime.timedelta(1)))], has_volume, has_weight)
        if last_avg_price > 0:
            self.result[product].update(
                {
                    f'L{row}': (this_avg_price - last_avg_price)
                    / last_avg_price
                    * 100
                }
            )
        if has_volume:
            last_avg_volume = get_avg_volume(qs, (self.last_week_start)), (self.last_week_end - datetime.timedelta(1)))
            this_avg_volume = get_avg_volume(qs, (self.this_week_start)), (self.this_week_end - datetime.timedelta(1)))
            self.result[product].update({f'T{row}': this_avg_volume})
            if last_avg_volume > 0:
                self.result[product].update(
                    {
                        f'U{row}': (this_avg_volume - last_avg_volume)
                        / last_avg_volume
                        * 100
                    }
                )
        if monitor_price:
            self.result[product].update({f'F{row}': monitor_price})
        self.result[product].update(
            {f'H{row}': this_avg_price, f'W{row}': last_avg_price}
        )

    def update_data(self, query_set, product, row):
        # if query_set.count():
        #     has_volume = query_set.filter(volume__isnull=False).count() > 0.8 * query_set.count()
        #     has_weight = query_set.filter(avg_weight__isnull=False).count() > 0.8 * query_set.count()
        # else:
        #     has_volume = False
        #     has_weight = False

        # if has_volume and has_weight:
        #     query_set = query_set.filter(Q(volume__gt=0) & Q(avg_weight__gt=0))

        # query_set = (query_set.values('date').annotate(
        #     year=Year('date'),
        #     month=Month('date'),
        #     day=Day('date')))
        
        # qs = query_set.annotate(
        #     avg_price=F('avg_price'),
        #     sum_volume=F('volume'),
        #     avg_avg_weight=F('avg_weight'),
        # )

        # qs = qs.order_by('date')
        qs, has_volume, has_weight = get_group_by_date_query_set(query_set)
        last_year_avg_price = get_avg_price(qs, has_volume, has_weight)
        if last_year_avg_price > 0:
            self.result[product].update({f'G{row}': last_year_avg_price})


    def update_rams(self, item, row):
        query_set = DailyTran.objects.filter(product__in=item.product_list(), source__in=item.sources())
        for i in range(7):
            week_day = self.this_week_start + datetime.timedelta(i)
            qs = query_set.filter(date__lte=week_day.date()).order_by('-date')
            if qs:
                qs = qs.first()
            else:
                continue
            if i == 0 or qs.date == week_day.date():
                self.result[item.product.name].update(
                    {f"{self.col_dict[f'{week_day.date()}']}{row}": qs.avg_price}
                )
            else:
                self.result[item.product.name].update(
                    {
                        f"{self.col_dict[f'{week_day.date()}']}{row}": qs.date.strftime(
                            '(%m/%d)'
                        )
                    }
                )

    def update_cattles(self, item, row):
        query_set = DailyTran.objects.filter(product__in=item.product_list())
        last_week_price = []
        this_week_price = []
        for i in range(7):
            week_day = self.this_week_start + datetime.timedelta(i)
            qs = query_set.filter(date__lte=week_day.date()).order_by('-date')
            if not qs:
                continue
            qs = qs.first()
            this_week_price.append(qs.avg_price)
            self.result[item.product.name].update(
                {f"{self.col_dict[f'{week_day.date()}']}{row}": qs.avg_price}
            )
        for i in range(1, 8):
            week_day = self.this_week_start - datetime.timedelta(i)
            qs = query_set.filter(date__lte=week_day.date()).order_by('-date')
            if qs:
                qs = qs.first()
                last_week_price.append(qs.avg_price)
        if len(last_week_price):
            last_week_avg_price = sum(last_week_price) / len(last_week_price)
            self.result[item.product.name].update({f'W{row}': last_week_avg_price})
        if len(this_week_price):
            this_week_avg_price = sum(this_week_price) / len(this_week_price)
            self.result[item.product.name].update({f'H{row}': this_week_avg_price})
        if len(last_week_price) and len(this_week_price):
            self.result[item.product.name].update(
                {
                    f'L{row}': (this_week_avg_price - last_week_avg_price)
                    / last_week_avg_price
                    * 100
                }
            )

    def report(self):
        watchlist = Watchlist.objects.filter(
            start_date__year=self.specify_day.year,
            start_date__month__lte=self.specify_day.month,
            end_date__month__gte=self.specify_day.month
        ).first()
        monitor = MonitorProfile.objects.filter(watchlist=watchlist, row__isnull=False)

        for item in monitor:
            # self.row_visible.append(item.row)
            query_set = DailyTran.objects.filter(product__in=item.product_list())

            # 因應措施是梨
            if self.specify_day.month in [5, 6]:
                if item.product.id == 50182:
                    # 56只抓豐水梨 50186
                    query_set = query_set.filter(product=50186)
            elif self.specify_day.month in [7, 8]:
                if item.product.id == 50182:
                    # 78只抓新興梨 50185
                    query_set = query_set.filter(product=50185)

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
            self._extract_data(item[1], WatchlistItem, item[0], None, self.specify_day)
            # self.row_visible.append(item[1])
            # watchlist_item = WatchlistItem.objects.filter(id=item[0]).first()
            # product = watchlist_item.product
            # query_set = DailyTran.objects.filter(product=product)
            # if watchlist_item.sources.all():
            #     query_set = query_set.filter(source__in=watchlist_item.sources.all())
            # self.get_data(query_set, product.name, item[1], None)
            # # last year avg_price of month
            # query_set = DailyTran.objects.filter(product=product,
            #                                     date__year=self.specify_day.year-1,
            #                                     date__month=self.specify_day.month)
            # if watchlist_item.sources.all():
            #     query_set = query_set.filter(source__in=watchlist_item.sources.all())
            # self.update_data(query_set, product.name, item[1])

        # 香蕉台北一二批發
        self._extract_data(73, Fruit, 50063, Source.objects.filter(id__in=[20001, 20002]), self.specify_day)
        # self.row_visible.append(73)
        # product = Fruit.objects.get(id=50063)
        # sources = Source.objects.filter(id__in=[20001, 20002])
        # query_set = DailyTran.objects.filter(product=product, source__in=sources)
        # self.get_data(query_set, f'{product.name}{product.type}', 73, None)
        # query_set = DailyTran.objects.filter(product=product, source__in=sources, date__year=self.specify_day.year-1, date__month=self.specify_day.month)
        # self.update_data(query_set, f'{product.name}{product.type}', 73)

        # 青香蕉下品()內銷)
        self._extract_data(72, Fruit, 59019, Source.objects.filter(id__in=range(10030,20001)), self.specify_day)
        # self.row_visible.append(72)
        # product = Fruit.objects.get(id=59019)
        # sources = Source.objects.filter(id__gte=10030, id__lte=20000)
        # query_set = DailyTran.objects.filter(product=product, source__in=sources)
        # self.get_data(query_set, '{}{}'.format(product.name, product.type), 72, None)
        # query_set = DailyTran.objects.filter(product=product, date__year=self.specify_day.year-1, date__month=self.specify_day.month)
        # self.update_data(query_set, '{}{}'.format(product.name, product.type), 72)

        # 2020/4/16 主管會報陳副主委要求花卉品項,農糧署建議新增香水百合 FS  
        self._extract_data(107, Flower, 60068, Source.objects.filter(id__in=[30001, 30002, 30003, 30004, 30005]), self.specify_day)
        # self.row_visible.append(107)
        # product = Flower.objects.get(id=60068)
        # sources = Source.objects.filter(id__in=[30001, 30002, 30003, 30004, 30005])
        # query_set = DailyTran.objects.filter(product=product, source__in=sources)
        # self.get_data(query_set, '{}{}'.format(product.name, product.type), 107, None)
        # query_set = DailyTran.objects.filter(product=product, date__year=self.specify_day.year-1, date__month=self.specify_day.month)
        # self.update_data(query_set, '{}{}'.format(product.name, product.type), 107)

    def _extract_data(self, row, model, product_id, sources=None, date=None):
        self.row_visible.append(row)
        if model == WatchlistItem:
            watchlist_item = model.objects.filter(id=product_id).first()
            product = watchlist_item.product
            if watchlist_item.sources.all():
                sources = watchlist_item.sources.all()
        else:
            product = model.objects.get(id=product_id)
        query_set = DailyTran.objects.filter(product=product)
        if sources:
            query_set = query_set.filter(source__in=sources)
        self.get_data(query_set, f'{product.name}{product.type}', row, None)
        if date:
            query_set = DailyTran.objects.filter(product=product, date__year=date.year-1, date__month=date.month)
            if sources:
                query_set = query_set.filter(source__in=sources)   
            self.update_data(query_set, f'{product.name}{product.type}', row)

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
        sheet_name = wb.sheetnames[0]
        sheet = wb[sheet_name]

        for i in range(7):
            sheet = self.input_sheet_date(sheet, i)
        sheet['G6'] = (
            f'{self.specify_day.year - 1912}\n年{self.specify_day.month}月\n平均價格'
        )
        last_week_range = f'{self.last_week_start.month}/{self.last_week_start.day}~{self.last_week_end.month}/{self.last_week_end.day}'
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
            # 依袁麗惠要求,日報取消品項底色識別
            # 第二階段隱藏品項欄位
            # td = sheet.cell(row=i, column=2)
            # A.品項欄位去除底色
            # td.fill = PatternFill(
            #     fill_type='solid',
            #     start_color='FFFFFF',
            #     end_color='FFFFFF'
            # )

        # 第二階段隱藏品項欄位後日報下方說明欄,依品項顯示月份對應調整資料來源文字說明處理
        for rows in sheet['A133:U148']:
            for cell in rows:
                # 資料來源字型統一為標楷體
                cell.font = Font(name='標楷體', size=13)
                row_no = cell.row
                if row_no > 134:
                    cell.value = None
        
        sheet.cell(row=133, column=1).value = sheet.cell(row=133, column=1).value.replace('本會', '本部')
        sheet.cell(row=134, column=1).value = sheet.cell(row=134, column=1).value.replace('本會', '本部')

        now_row = 135
        # 一般農產品的資料來源說明欄位處理
        for i in desc_1:
            item_name = i[0]
            desc_1_text = i[1]

            # append_desc
            if item_name in self.item_desc:
                td = sheet.cell(row=now_row, column=1)
                tmp = (now_row == 135 and '3.') or '   '
                td.value = f"{tmp}{desc_1_text}；"
                now_row += 1
        td = sheet.cell(row=now_row-1, column=1)
        td.value = td.value.replace('；', '—農產品價格查報，本部農糧署。')
        desc_2_tmp = []
        pn = 4
        for item_name in desc_2:
            if item_name in self.item_desc:
                if item_name == '柿子':
                    desc_2_tmp.append('甜柿')
                else:
                    desc_2_tmp.append(item_name)
        if desc_2_tmp:
            td = sheet.cell(row=now_row, column=1)
            desc_2_text = '4.'+'、'.join(desc_2_tmp) + \
                '交易量價(東勢果菜市場價格)－農產品行情報導，本部農糧署。'
            td.value = desc_2_text
            now_row += 1
            pn += 1
        # 其餘花卉,畜禽,水產類的資料來源說明欄位處理
        for p in desc_3:
            td = sheet.cell(row=now_row, column=1)
            td.value = f"{str(pn)}.{p}"
            pn += 1
            now_row += 1

        return wb

    def __call__(self, output_dir=settings.BASE_DIR):
        date = self.specify_day + datetime.timedelta(1)
        file_name = f'{self.roc_date_format(self.this_week_start)}-{self.roc_date_format(self.this_week_end)}價格{WEEKDAY.get(date.weekday())}.xlsx'

        file_path = Path(output_dir, file_name)

        self.report()
        sheet = self.get_sheet()
        sheet.save(file_path)

        return file_name, file_path
