import pandas as pd 
import numpy as np
import psycopg2
from datetime import date
from sqlalchemy import create_engine
from _pydecimal import Decimal, Context, ROUND_HALF_UP
from django.conf import settings
from apps.configs.models import AbstractProduct, Last5YearsItems
from functools import reduce
import operator
import logging

db_logger = logging.getLogger('aprp')

#連結資料庫相關設定
myDBname = settings.DATABASES['default']['NAME']
my_uesrname = settings.DATABASES['default']['USER']
my_pwd = settings.DATABASES['default']['PASSWORD']
my_host = settings.DATABASES['default']['HOST']
my_port = settings.DATABASES['default']['PORT']

con = psycopg2.connect(database=myDBname, user=my_uesrname, password=my_pwd, host=my_host, port=my_port) 
engine = create_engine('postgresql://'+my_uesrname+':'+my_pwd+'@'+my_host+':'+str(my_port)+'/'+myDBname, echo=False) 

class Last5YearsReportFactory(object):
    def __init__(self, product_id, source, is_hogs=False, is_rams=False):
        self.product_id = product_id
        self.source = source
        self.today = date.today()
        self.today_year = self.today.year
        self.today_month = self.today.month
        self.last_5_years_ago = self.today_year - 5
        self.last_year = self.today_year - 1
        self.is_hogs = is_hogs
        self.is_rams = is_rams

    def get_table(self):
        #查詢品項五年內所有日期的數據總表

        # 父類品項中尋找各子類品項(以下程式碼從 dashboard/utils.py/product_selector_base_extra_context 節錄過來修改)
        product_qs = AbstractProduct.objects.filter(id__in=self.product_id)
        products = product_qs.exclude(track_item=False)
        
        if product_qs.filter(track_item=False):
            sub_products = reduce(
                operator.or_,
                (product.children().filter(track_item=True) for product in product_qs.filter(track_item=False))
            )
            products = products | sub_products

        if product_qs.first().track_item is False and product_qs.first().config.id == 13:
            products = product_qs
        #(以上程式碼從 dashboard/utils.py/product_selector_base_extra_context 節錄過來修改)
        self.all_product_id_list = [i.id for i in products]
        all_date_list = [f'{self.last_5_years_ago}-01-01',self.today.strftime("%Y-%m-%d")]
        table = pd.read_sql_query("select product_id, source_id, avg_price, avg_weight, volume, date from dailytrans_dailytran INNER JOIN unnest(%(all_product_id_list)s) as pid ON pid=dailytrans_dailytran.product_id where ((date between %(all_date_list00)s and %(all_date_list01)s))", params={'all_product_id_list':self.all_product_id_list,'all_date_list00':all_date_list[0],'all_date_list01':all_date_list[1]},con=engine)

        table['date'] = pd.to_datetime(table['date'], format='%Y-%m-%d')
        return table

    def result(self,table):
        source_list = self.source
        product_data_dict = {}
        avgprice_dict = {}
        avgvolume_dict = {}
        avgweight_dict = {}
        avgvolumeweight_dict = {}
        has_volume = False
        has_weight = False

        # 近五年各月數據
        for y in range(self.last_5_years_ago,self.today_year+1):
            avgprice_month_list = []
            avgvolume_month_list = []
            avgweight_month_list = []
            avgvolumeweight_month_list = []
            totalprice, totalvolume, totalweight, totalvolumeweight = 0, 0, 0, 0
            dayswithprice, dayswithvolume, dayswithweight, dayswithvolumeweight = 0, 0, 0, 0

            end_month = 13
            if y == self.today_year:
                end_month = self.today_month + 1

            for m in range(1,end_month):
                if source_list:
                    one_month_data = table[(pd.to_datetime(table['date']).dt.year == y) & (pd.to_datetime(table['date']).dt.month == m) ].query("source_id == @source_list")
                else:
                    if self.is_hogs: #毛豬(規格豬)計算需排除澎湖市場
                        one_month_data = table[(pd.to_datetime(table['date']).dt.year == y) & (pd.to_datetime(table['date']).dt.month == m) ].query("source_id != 40050")
                    else:
                        one_month_data = table[(pd.to_datetime(table['date']).dt.year == y) & (pd.to_datetime(table['date']).dt.month == m) ]

                if one_month_data['avg_price'].any():
                    has_volume = one_month_data['volume'].notna().sum() / one_month_data['avg_price'].count() > 0.8
                    has_weight = one_month_data['avg_weight'].notna().sum() / one_month_data['avg_price'].count() > 0.8
                else:
                    has_volume = False
                    has_weight = False
                
                if has_volume and has_weight:
                    one_month_totalprice = (one_month_data['avg_price']*one_month_data['avg_weight']*one_month_data['volume']).sum()
                    one_month_totalweight = (one_month_data['avg_weight']*one_month_data['volume']).sum()
                    one_month_totalvolume = (one_month_data['volume']).sum()
                    totalprice += one_month_totalprice
                    totalweight += one_month_totalweight
                    avgprice = one_month_totalprice / one_month_totalweight
                    avgweight = one_month_totalweight / one_month_totalvolume
                    
                    if self.is_rams : #羊的交易量,
                        totalvolume += one_month_totalvolume
                        avgvolume = one_month_data.groupby('date').sum()['volume'].mean()

                    elif self.is_hogs: #毛豬交易量為頭數
                        totalvolume += one_month_totalvolume / 1000
                        totalvolumeweight += one_month_totalweight
                        avgvolume = one_month_data.groupby('date').sum()['volume'].mean() / 1000
                        avgweight = avgweight
                        avgvolumeweight = (avgweight*avgvolume*1000) / 1000
                    else:   #環南市場-雞的交易量
                        # avgvolume = (one_month_data['avg_weight']*one_month_data['volume']).sum()/(one_month_data['volume']).sum()
                        totalvolume += one_month_totalvolume
                        avgvolume = one_month_data.groupby('date').sum()['volume'].mean()
                        avgweight = one_month_data.groupby('date').sum()['avg_weight'].mean()
                    dayswithprice += (one_month_data['avg_weight']*one_month_data['volume']).sum()
                    dayswithweight += one_month_data['volume'].sum()
                    dayswithvolume += one_month_data.groupby('date').sum()['volume'].count()
                    dayswithvolumeweight += one_month_data.groupby('date').sum()['volume'].count()
                elif has_volume:
                    totalprice += (one_month_data['avg_price']*one_month_data['volume']).sum()
                    totalvolume += one_month_data.groupby('date').sum()['volume'].sum() / 1000
                    avgprice=(one_month_data['avg_price']*one_month_data['volume']).sum()/one_month_data['volume'].sum()
                    avgvolume = one_month_data.groupby('date').sum()['volume'].mean() / 1000
                    dayswithprice += (one_month_data['volume'].sum())
                    dayswithvolume += one_month_data.groupby('date').sum()['volume'].count()

                else:
                    totalprice += one_month_data['avg_price'].sum()
                    avgprice = one_month_data['avg_price'].mean()
                    avgvolume = np.nan
                    avgweight = np.nan
                    dayswithprice += one_month_data['avg_price'].count()

                avgprice_month_list.append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgprice)))
                # if has_volume:    # 特定產品於某年度9~12月份才開始有數據,原條件判斷會導致該年度9~12月份的數據變成1~4月   
                avgvolume_month_list.append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgvolume)))
                if self.is_hogs and has_weight:
                    avgweight_month_list.append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgweight)))
                    avgvolumeweight_month_list.append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgvolumeweight)))
                elif has_weight:
                    avgweight_month_list.append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgweight)))

            # insert yearly avg price, volume, weight and volume*weight to dict
            avgprice_year = totalprice / dayswithprice
            avgprice_month_list.insert(0, float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgprice_year)))
            if [x for x in avgvolume_month_list if x==x] != []:
                avgvolume_year = totalvolume / dayswithvolume
                avgvolume_month_list.insert(0, float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgvolume_year)))
            else:
                avgvolume_month_list.insert(0, np.nan)
            avgprice_dict[str(y-1911)+'年'] = avgprice_month_list
            # if has_volume:    # 特定產品於某年度9~12月份才開始有數據,原條件判斷會導致該年度9~12月份的數據變成1~4月
            avgvolume_dict[str(y-1911)+'年'] = avgvolume_month_list
            
            if self.is_hogs and has_weight:
                avgweight_year = totalweight / dayswithweight
                avgweight_month_list.insert(0, float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgweight_year)))
                avgweight_dict[str(y-1911)+'年'] = avgweight_month_list
                avgvolumeweight_yaer = totalvolumeweight / dayswithvolumeweight / 1000
                avgvolumeweight_month_list.insert(0, float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgvolumeweight_yaer)))
                avgvolumeweight_dict[str(y-1911)+'年'] = avgvolumeweight_month_list
            elif has_weight:
                avgweight_year = totalweight / dayswithweight
                avgweight_month_list.insert(0, float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgweight_year)))
                avgweight_dict[str(y-1911)+'年'] = avgweight_month_list

        product_data_dict[self.all_product_id_list[0]] = {'avgprice' : avgprice_dict, 'avgvolume' : avgvolume_dict, 'avgweight' : avgweight_dict, 'avgvolumeweight' : avgvolumeweight_dict}

        # 近五年平均值
        last_5_years_avg_data = {}
        last_5_years_avg_data['avgprice'] = {}
        last_5_years_avg_data['avgvolume'] = {}
        last_5_years_avg_data['avgweight'] = {}
        last_5_years_avg_data['avgvolumeweight'] = {}
        has_volume = False
        has_weight = False
        last_5_years_avgprice_list = [np.nan]
        last_5_years_avgvolume_list = [np.nan]
        last_5_years_avgweight_list = [np.nan]
        last_5_years_avgvolumeweight_list = [np.nan]
        avgprice_data = pd.DataFrame()
        avgvolume_data = pd.DataFrame()
        avgweight_data = pd.DataFrame()
        avgvolumeweight_data = pd.DataFrame()

        for m in range(1,13):
            avgvolume_temp_list = []

            if source_list:
                last_5_years_onemonth_table = table[(pd.to_datetime(table['date']).dt.year >= self.last_5_years_ago) & (pd.to_datetime(table['date']).dt.year <= self.last_year) & (pd.to_datetime(table['date']).dt.month == m)].query("source_id == @source_list")
            else:
                if self.is_hogs: #毛豬(規格豬)計算需排除澎湖市場
                    last_5_years_onemonth_table = table[(pd.to_datetime(table['date']).dt.year >= self.last_5_years_ago) & (pd.to_datetime(table['date']).dt.year <= self.last_year) & (pd.to_datetime(table['date']).dt.month == m)].query("source_id != 40050")
                else:
                    last_5_years_onemonth_table = table[(pd.to_datetime(table['date']).dt.year >= self.last_5_years_ago) & (pd.to_datetime(table['date']).dt.year <= self.last_year) & (pd.to_datetime(table['date']).dt.month == m)]

            if last_5_years_onemonth_table['avg_price'].any():
                has_volume = last_5_years_onemonth_table['volume'].notna().sum() / last_5_years_onemonth_table['avg_price'].count() > 0.8
                has_weight = last_5_years_onemonth_table['avg_weight'].notna().sum() / last_5_years_onemonth_table['avg_price'].count() > 0.8
            else:
                has_volume = False
                has_weight = False
            
            last_5_years_onemonth_table=last_5_years_onemonth_table.copy()    #此步驟為避免後續 dataframe 計算過程中出現警告訊息

            if has_volume and has_weight:
                last_5_years_onemonth_table['pvw'] = last_5_years_onemonth_table['avg_price'] * last_5_years_onemonth_table['volume'] * last_5_years_onemonth_table['avg_weight']
                last_5_years_onemonth_table['vw'] = last_5_years_onemonth_table['volume'] * last_5_years_onemonth_table['avg_weight']
                one_month_avgprice = last_5_years_onemonth_table.groupby('date')['pvw'].sum()/last_5_years_onemonth_table.groupby('date')['vw'].sum()
                one_month_avgweight = last_5_years_onemonth_table.groupby('date')['vw'].sum()/last_5_years_onemonth_table.groupby('date')['volume'].sum()
                one_month_sumvolume = last_5_years_onemonth_table.groupby('date')['volume'].sum()
                avgprice_one_month = (one_month_avgprice*one_month_sumvolume*one_month_avgweight).sum()/(one_month_sumvolume*one_month_avgweight).sum()
                avgweight_one_month = (one_month_sumvolume*one_month_avgweight).sum()/(one_month_sumvolume).sum()
                last_5_years_avg_data['avgprice'][m] = float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgprice_one_month))

                if self.is_rams: #羊的交易量,
                    last_5_years_avg_data['avgvolume'][m] = last_5_years_onemonth_table.groupby('date').sum()['volume'].mean()
                    last_5_years_avg_data['avgweight'][m] = float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgweight_one_month))
                elif self.is_hogs: #毛豬交易量為頭數
                    last_5_years_avg_data['avgvolume'][m] = last_5_years_onemonth_table.groupby('date').sum()['volume'].mean() / 1000
                    last_5_years_avg_data['avgweight'][m] = float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgweight_one_month))
                    one_month_avgvolumeweight = (last_5_years_onemonth_table.groupby('date')['vw'].sum()).mean() / 1000
                    last_5_years_avg_data['avgvolumeweight'][m] = float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(one_month_avgvolumeweight))
                    last_5_years_avgvolumeweight_list.append(last_5_years_avg_data['avgvolumeweight'][m])
                else:
                    last_5_years_avg_data['avgvolume'][m] = last_5_years_onemonth_table.groupby('date').sum()['volume'].mean()
                    last_5_years_avg_data['avgweight'][m] = last_5_years_onemonth_table.groupby('date').sum()['avg_weight'].mean()

                last_5_years_avgprice_list.append(last_5_years_avg_data['avgprice'][m])
                last_5_years_avgvolume_list.append(last_5_years_avg_data['avgvolume'][m])
                last_5_years_avgweight_list.append(last_5_years_avg_data['avgweight'][m])
                
                    
            elif has_volume:
                #平均價
                last_5_years_onemonth_table['pv']=last_5_years_onemonth_table['avg_price'] * last_5_years_onemonth_table['volume']
                one_month_avgprice = last_5_years_onemonth_table.groupby('date')['pv'].sum()/last_5_years_onemonth_table.groupby('date')['volume'].sum()
                one_month_sumvolume = last_5_years_onemonth_table.groupby('date').sum()['volume'].values
                avgprice_one_month = (one_month_avgprice*one_month_sumvolume).sum()/one_month_sumvolume.sum()
                last_5_years_avg_data['avgprice'][m] = float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgprice_one_month))

                last_5_years_avgprice_list.append(last_5_years_avg_data['avgprice'][m])

                #平均量
                last_5_years_avgvolume_month = last_5_years_onemonth_table.groupby('date').sum()['volume'].values
                for j in last_5_years_avgvolume_month:
                    avgvolume_temp_list.append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(j)))

                last_5_years_avg_data['avgvolume'][m] = sum(avgvolume_temp_list) / len(avgvolume_temp_list) / 1000
                last_5_years_avgvolume_list.append(last_5_years_avg_data['avgvolume'][m])

            else:
                if last_5_years_onemonth_table.groupby('date').mean()['avg_price'].values.any():
                    one_month_avgprice = last_5_years_onemonth_table.groupby('date').mean()['avg_price'].values.mean()
                    last_5_years_avg_data['avgprice'][m] = one_month_avgprice
                    last_5_years_avgprice_list.append(last_5_years_avg_data['avgprice'][m])
                    has_price = True
                else:
                    last_5_years_avgprice_list.append(np.nan)
                    has_price = False
                
                # 為避免list對應月份數量錯誤,缺少數值的月份補空值
                last_5_years_avgvolume_list.append(np.nan)
                last_5_years_avgweight_list.append(np.nan)
                last_5_years_avgvolumeweight_list.append(np.nan)

        columns_name = ['年平均', '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
        avgprice_data = pd.DataFrame.from_dict(product_data_dict[self.all_product_id_list[0]]['avgprice'], orient='index')
        avgprice_data.columns = columns_name
        avgprice_data.loc['近五年平均'] = last_5_years_avgprice_list
        avgprice_data = avgprice_data.round(2)

        if pd.isna(product_data_dict[self.all_product_id_list[0]]['avgvolume']):
            avgvolume_data = pd.DataFrame.from_dict(product_data_dict[self.all_product_id_list[0]]['avgvolume'], orient='index')
            avgvolume_data.columns = columns_name
            avgvolume_data.loc['近五年平均'] = last_5_years_avgvolume_list
            avgvolume_data = avgvolume_data.round(3)

        if self.is_hogs and product_data_dict[self.all_product_id_list[0]]['avgweight']:
            avgweight_data = pd.DataFrame.from_dict(product_data_dict[self.all_product_id_list[0]]['avgweight'], orient='index')
            avgweight_data.columns = columns_name
            avgweight_data.loc['近五年平均'] = last_5_years_avgweight_list
            avgweight_data = avgweight_data.round(3)
            
            avgvolumeweight_data = pd.DataFrame.from_dict(product_data_dict[self.all_product_id_list[0]]['avgvolumeweight'], orient='index')
            avgvolumeweight_data.columns = columns_name
            avgvolumeweight_data.loc['近五年平均'] = last_5_years_avgvolumeweight_list
            avgvolumeweight_data = avgvolumeweight_data.round(3)
        elif product_data_dict[self.all_product_id_list[0]]['avgweight']:
            avgweight_data = pd.DataFrame.from_dict(product_data_dict[self.all_product_id_list[0]]['avgweight'], orient='index')
            avgweight_data.columns = columns_name
            avgweight_data.loc['近五年平均'] = last_5_years_avgweight_list
            avgweight_data = avgweight_data.round(3)

        return avgprice_data, avgvolume_data, avgweight_data, avgvolumeweight_data


    def __call__(self):
        #獲取完整交易表
        table = self.get_table()

        if not table.empty:
            return self.result(table)
        else:
            db_logger.error(f'DB query error : product_id_list = {self.all_product_id_list}; source_list = {self.source}', extra={'type_code': 'LOT-last5yearsreport'})



