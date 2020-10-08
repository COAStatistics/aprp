import pandas as pd 
import psycopg2
import sxtwl #陽曆陰曆轉換套件
from datetime import datetime,timedelta,date
from sqlalchemy import create_engine
from _pydecimal import Decimal, Context, ROUND_HALF_UP
import time
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter

from pathlib import Path
from django.conf import settings
from apps.configs.models import FestivalItems

#Django ORM 模式
# from apps.dailytrans.models import DailyTran
# from django.db.models import Q

#連結資料庫相關設定
myDBname = settings.DATABASES['default']['NAME']
my_uesrname = settings.DATABASES['default']['USER']
my_pwd = settings.DATABASES['default']['PASSWORD']
my_host = settings.DATABASES['default']['HOST']
my_port = settings.DATABASES['default']['PORT']

con = psycopg2.connect(database=myDBname, user=my_uesrname, password=my_pwd, host=my_host, port=my_port) 
engine = create_engine('postgresql://'+my_uesrname+':'+my_pwd+'@'+my_host+':'+str(my_port)+'/'+myDBname, echo=False) 


class FestivalReportFactory(object):
    def __init__(self, rocyear, festival, oneday=None, special_day=date.today()-timedelta(days=1)):
        self.year = int(rocyear) + 1911
        self.roc_year = self.year - 1911
        self.roc_before5years = self.roc_year -5
        self.festival = festival
        self.result_data = dict()
        self.seafood_id_list = []
        self.Chinese_New_Year_dict = dict() #春節_西元年
        self.Dragon_Boat_Festival_dict = dict() #端午節_西元年
        self.Mid_Autumn_Festival_dict = dict() #中秋節_西元年
        self.ROC_Chinese_New_Year_dict = dict() #春節_民國年
        self.ROC_Dragon_Boat_Festival_dict = dict() #端午節_民國年
        self.ROC_Mid_Autumn_Festival_dict = dict() #中秋節_民國年
        self.roc_date_range = dict()
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.all_product_id = set()
        self.product_dict = dict()
        self.pid = FestivalItems.objects.filter(festivalname__id__contains=self.festival)
        for i in self.pid:
            self.product_dict[i.name]=[]
            for j in i.product_id.all():
                self.product_dict[i.name].append(j.id)
                self.all_product_id.add(j.id)
        self.all_product_id_list = list(self.all_product_id)
        self.oneday = oneday
        if self.oneday:
            self.special_day = special_day
            self.special_day_year = self.special_day.split('-')[0]
        self.table = ''
        self.all_date_list = list()
        

    def festival_date(self, year,  festival):
        # 日曆庫實例化
        lunar = sxtwl.Lunar()

        for y in range(self.roc_before5years,self.roc_year+1):
            #陰曆轉陽曆
            if self.festival ==1:
                lunarday='{}-01-01'.format(int(y)+1911) #農曆春節
            elif self.festival ==2:
                lunarday='{}-05-05'.format(int(y)+1911) #農曆端午節
            elif self.festival ==3:
                lunarday='{}-08-15'.format(int(y)+1911) #農曆中秋節
            lunarday_list = lunarday.split('-')
            solar_day = lunar.getDayByLunar((int)(lunarday_list[0]),(int)(lunarday_list[1]),(int)(lunarday_list[2])) 
            importfestival="{0}-{1}-{2}".format(solar_day.y,solar_day.m,solar_day.d)
            festival_day=datetime.strptime(importfestival, "%Y-%m-%d")
            b1w_end = festival_day - timedelta(days=1) #前一周結束日期
            b1w_start = b1w_end - timedelta(days=6) #前一周開始日期
            b2w_end = b1w_start - timedelta(days=1) #前兩周結束日期
            b2w_start = b2w_end - timedelta(days=6) #前兩周開始日期
            b3w_end = b2w_start - timedelta(days=1) #前三周結束日期
            b3w_start = b3w_end - timedelta(days=6) #前三周開始日期
            b4w_end = b3w_start - timedelta(days=1) #前四周結束日期
            b4w_start = b4w_end - timedelta(days=6) #前四周開始日期
            a1w_start = festival_day #節後一周開始日期暨節日當天
            a1w_end = festival_day + timedelta(days=6) #節後一周結束日期
            a2w_start = a1w_end + timedelta(days=1) #節後二周開始日期天
            a2w_end = a2w_start + timedelta(days=6) #節後二周結束日期
            a3w_start = a2w_end + timedelta(days=1) #節後三周開始日期
            a3w_end = a3w_start + timedelta(days=6) #節後三周結束日期
            a4w_start = a3w_end + timedelta(days=1) #節後四周開始日期
            a4w_end = a4w_start + timedelta(days=6) #節後四周結束日期
            begin_date = b4w_start
            last_date = a4w_end
            self.all_date_list.append([begin_date.date(),last_date.date()])

            if y == self.roc_year:    #今年度新增最近1日的日期區間
                if self.festival ==1:
                    self.Chinese_New_Year_dict[str(y)]=['{0}~{1}'.format(b4w_start.date(),b4w_end.date()),'{0}~{1}'.format(b3w_start.date(),b3w_end.date()),'{0}~{1}'.format(b2w_start.date(),b2w_end.date()),'{0}~{1}'.format(b1w_start.date(),b1w_end.date()),'{0}~{1}'.format(a1w_start.date(),a1w_end.date()),'{0}~{1}'.format(a2w_start.date(),a2w_end.date()),'{0}~{1}'.format(a3w_start.date(),a3w_end.date()),'{0}~{1}'.format(a4w_start.date(),a4w_end.date()),'{0}~{1}'.format(self.yesterday,self.yesterday)]
                elif self.festival ==2:
                    self.Dragon_Boat_Festival_dict[str(y)]=['{0}~{1}'.format(b4w_start.date(),b4w_end.date()),'{0}~{1}'.format(b3w_start.date(),b3w_end.date()),'{0}~{1}'.format(b2w_start.date(),b2w_end.date()),'{0}~{1}'.format(b1w_start.date(),b1w_end.date()),'{0}~{1}'.format(a1w_start.date(),a1w_end.date()),'{0}~{1}'.format(a2w_start.date(),a2w_end.date()),'{0}~{1}'.format(a3w_start.date(),a3w_end.date()),'{0}~{1}'.format(a4w_start.date(),a4w_end.date()),'{0}~{1}'.format(self.yesterday,self.yesterday)]
                elif self.festival ==3:
                    self. Mid_Autumn_Festival_dict[str(y)]=['{0}~{1}'.format(b4w_start.date(),b4w_end.date()),'{0}~{1}'.format(b3w_start.date(),b3w_end.date()),'{0}~{1}'.format(b2w_start.date(),b2w_end.date()),'{0}~{1}'.format(b1w_start.date(),b1w_end.date()),'{0}~{1}'.format(a1w_start.date(),a1w_end.date()),'{0}~{1}'.format(a2w_start.date(),a2w_end.date()),'{0}~{1}'.format(a3w_start.date(),a3w_end.date()),'{0}~{1}'.format(a4w_start.date(),a4w_end.date()),'{0}~{1}'.format(self.yesterday,self.yesterday)]
            else:
                if self.festival ==2:
                    self.Chinese_New_Year_dict[str(y)]=['{0}~{1}'.format(b4w_start.date(),b4w_end.date()),'{0}~{1}'.format(b3w_start.date(),b3w_end.date()),'{0}~{1}'.format(b2w_start.date(),b2w_end.date()),'{0}~{1}'.format(b1w_start.date(),b1w_end.date()),'{0}~{1}'.format(a1w_start.date(),a1w_end.date()),'{0}~{1}'.format(a2w_start.date(),a2w_end.date()),'{0}~{1}'.format(a3w_start.date(),a3w_end.date()),'{0}~{1}'.format(a4w_start.date(),a4w_end.date())]
                elif self.festival ==2:
                    self.Dragon_Boat_Festival_dict[str(y)]=['{0}~{1}'.format(b4w_start.date(),b4w_end.date()),'{0}~{1}'.format(b3w_start.date(),b3w_end.date()),'{0}~{1}'.format(b2w_start.date(),b2w_end.date()),'{0}~{1}'.format(b1w_start.date(),b1w_end.date()),'{0}~{1}'.format(a1w_start.date(),a1w_end.date()),'{0}~{1}'.format(a2w_start.date(),a2w_end.date()),'{0}~{1}'.format(a3w_start.date(),a3w_end.date()),'{0}~{1}'.format(a4w_start.date(),a4w_end.date())]
                elif self.festival ==3:
                    self.Mid_Autumn_Festival_dict[str(y)]=['{0}~{1}'.format(b4w_start.date(),b4w_end.date()),'{0}~{1}'.format(b3w_start.date(),b3w_end.date()),'{0}~{1}'.format(b2w_start.date(),b2w_end.date()),'{0}~{1}'.format(b1w_start.date(),b1w_end.date()),'{0}~{1}'.format(a1w_start.date(),a1w_end.date()),'{0}~{1}'.format(a2w_start.date(),a2w_end.date()),'{0}~{1}'.format(a3w_start.date(),a3w_end.date()),'{0}~{1}'.format(a4w_start.date(),a4w_end.date())]

        #西元年日期區間轉換為民國年日期區間
        if self.festival ==1:
            self.ROC_Chinese_New_Year_dict = self.year2rocyear(self.Chinese_New_Year_dict)
        elif self.festival ==2:
            self.ROC_Dragon_Boat_Festival_dict = self.year2rocyear(self.Dragon_Boat_Festival_dict)
        elif self.festival ==3:
            self.ROC_Mid_Autumn_Festival_dict = self.year2rocyear(self.Mid_Autumn_Festival_dict)


    #西元年日期區間轉為民國年日期區間
    def year2rocyear(self, date_range):
        if date_range:
            j=len(date_range.values())-1
            for k,v in date_range.items():
                temp_list=[]
                for i in range(len(v)):
                    d=v[i].replace('-','/').replace('{}/'.format(int(self.year)-j),'')
                    temp_list.append(d)
                j=j-1
                self.roc_date_range[k]=temp_list
        else:
            self.roc_date_range = {}
        return self.roc_date_range

    def get_table(self):

        if self.oneday:
            #Pandas dataframe 模式
            table = pd.read_sql_query(f"select product_id, source_id, avg_price, volume, date from dailytrans_dailytran INNER JOIN unnest(ARRAY{self.all_product_id_list}) as pid ON pid=dailytrans_dailytran.product_id where date = '{self.special_day}' ",con=engine)

            #Django ORM 模式
            # table = DailyTran.objects.filter(product__in=self.all_product_id_list).filter(date = self.special_day)

        else:
            #Pandas dataframe 模式
            table = pd.read_sql_query(f"select product_id, source_id, avg_price, volume, date from dailytrans_dailytran INNER JOIN unnest(ARRAY{self.all_product_id_list}) as pid ON pid=dailytrans_dailytran.product_id where ((date between '{self.all_date_list[0][0]}' and '{self.all_date_list[0][1]}') or (date between '{self.all_date_list[1][0]}' and '{self.all_date_list[1][1]}') or (date between '{self.all_date_list[2][0]}' and '{self.all_date_list[2][1]}') or (date between '{self.all_date_list[3][0]}' and '{self.all_date_list[3][1]}') or (date between '{self.all_date_list[4][0]}' and '{self.all_date_list[4][1]}') or (date between '{self.all_date_list[5][0]}' and '{self.all_date_list[5][1]}'))",con=engine)

            #Django ORM 模式
            # table = DailyTran.objects.filter(product__in=self.all_product_id_list).filter(Q((date >= self.all_date_list[0][0]) & (date <= self.all_date_list[0][1])) | Q((date >= self.all_date_list[1][0]) & (date <= self.all_date_list[1][1])) | Q((date >= self.all_date_list[2][0]) & (date <= self.all_date_list[2][1])) | Q((date >= self.all_date_list[3][0]) & (date <= self.all_date_list[3][1])) | Q((date >= self.all_date_list[4][0]) & (date <= self.all_date_list[4][1])) | Q((date >= self.all_date_list[5][0]) & (date <= self.all_date_list[5][1])) )
        
        #Pandas dataframe 模式需要此兩行轉換類型
        table['source_id'] = table['source_id'].fillna(0).astype(int)
        table['date'] = table['date'].astype(str)

        return table


    def result(self, festival, product_id, source_id):
        self.result_data[str(product_id)]={}
        if self.oneday:
            self.result_data[str(product_id)][str(self.special_day_year)]=[]

            if source_id:
                #Pandas dataframe 模式
                df_product_id = self.table.query(f'product_id in @product_id and (source_id in @source_id)')

                #Django ORM 模式
                # df_product_id = self.table.filter(product__in=product_id).filter(source__in=source_id)
            else:
                #Pandas dataframe 模式
                df_product_id = self.table.query(f'product_id in @product_id')

                #Django ORM 模式
                # df_product_id = self.table.filter(product__in=product_id)

            #Pandas dataframe 模式
            if df_product_id['volume'].sum() == 0:
                avgprice=df_product_id['avg_price'].mean()
            else:
                avgprice=(df_product_id['avg_price']*df_product_id['volume']).sum()/df_product_id['volume'].sum()
            
            #Django ORM 模式
            # total_price = list()
            # total_volume = list()
            # if df_product_id.count():
            #     if df_product_id.filter(volume__isnull=False).count() / df_product_id.count() > 0.8:
            #         for q in df_product_id:
            #             total_price.append(q.avg_price * q.volume)
            #             total_volume.append(q.volume)
            #             avgprice = sum(total_price) / sum(total_volume) if len(total_volume) else 0
            #     else:
            #         for q in df_product_id:
            #             total_price.append(q.avg_price)
            #             avgprice = sum(total_price) / len(total_price) if len(total_price) else 0
            # else:
            #     avgprice = 'nan'

            self.result_data[str(product_id)][str(self.special_day_year)].append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgprice)))

        else:
            for y in range(self.roc_before5years,self.roc_year+1):
                self.result_data[str(product_id)][str(y)]=[]

            for y in range(self.roc_before5years,self.roc_year+1):
                if festival ==1:
                    date_range = self.Chinese_New_Year_dict[str(y)]
                if festival ==2:
                    date_range = self.Dragon_Boat_Festival_dict[str(y)]
                if festival ==3:
                    date_range = self.Mid_Autumn_Festival_dict[str(y)]

                for d in date_range:
                    start_date = datetime.strptime("{}".format(d.split('~')[0]), "%Y-%m-%d").date()
                    end_date = datetime.strptime("{}".format(d.split('~')[1]), "%Y-%m-%d").date()

                    if source_id:
                        df_product_id = self.table.query(f'product_id in @product_id and date >= "{start_date}" and date <= "{end_date}" and (source_id in @source_id)')
                        # df_product_id = self.table.filter(product__in=product_id).filter(source__in=source_id).filter(date >=start_date).filter(date <= end_date)
                        
                    else:
                        df_product_id = self.table.query(f'product_id in @product_id and date >= "{start_date}" and date <= "{end_date}"')
                        # df_product_id = self.table.filter(product__in=product_id).filter(date >=start_date).filter(date <= end_date)

                    if df_product_id['volume'].sum() == 0:
                        avgprice=df_product_id['avg_price'].mean()
                    else:
                        avgprice=(df_product_id['avg_price']*df_product_id['volume']).sum()/df_product_id['volume'].sum()

                    # total_price = list()
                    # total_volume = list()
                    # if df_product_id.count():
                    #     if df_product_id.filter(volume__isnull=False).count() / df_product_id.count() > 0.8:
                    #         for q in df_product_id:
                    #             total_price.append(q.avg_price * q.volume)
                    #             total_volume.append(q.volume)
                    #             avgprice = sum(total_price) / sum(total_volume) if len(total_volume) else 0
                    #     else:
                    #         for q in df_product_id:
                    #             total_price.append(q.avg_price)
                    #             avgprice = sum(total_price) / len(total_price) if len(total_price) else 0
                    # else:
                    #     avgprice = 'nan'
                    self.result_data[str(product_id)][str(y)].append(float(Context(prec=28, rounding=ROUND_HALF_UP).create_decimal(avgprice)))
            
        return self.result_data

    def trimmean(self, arr):
        arr_min = arr.min()
        arr_max = arr.max()
        arr_sum = arr.sum()
        arr_trimmean = (arr_sum - arr_max - arr_min)/(len(arr)-2)
        return arr_trimmean

    def data2pandas2save(self, festival, product_dict, result_data):
        year_df = pd.Series(self.result_data.values())
        index_df = pd.Series(list(self.result_data.keys()))
        df1 = pd.DataFrame(index_df,index=[i for i in range(0,len(self.product_dict.keys()))])
        df2 = pd.DataFrame(list(year_df[0]),index=[i for i in range(0,len(self.product_dict.keys()))])
        df3 = pd.merge(df1,df2, left_index =True, right_index =True, how='outer')
        df3.columns.values[0]='農產品'
        for index, row in df3.iterrows():
            product_name = [k for k in list(self.product_dict.keys())][index]
            df3.loc[index,'農產品'] = product_name

        Row_list =[]
        for index, rows in df3.iterrows(): 
            data_list = []
            for y in range(self.roc_before5years,self.roc_year+1):
                data_list.append(rows[str(y)])
            l = [y for x in data_list for y in x]
            Row_list.append(l)

        columns=[]
        for y in range(self.roc_before5years,self.roc_year+1):
            if y == self.roc_year:
                for i in range(0,9):
                    temp_list=[]
                    if i ==0:
                        temp='節前四周'
                    elif i ==1:
                        temp='節前三周'
                    elif i ==2:
                        temp='節前二周'
                    elif i ==3:
                        temp='節前一周'
                    elif i ==4:
                        temp='節後一周'
                    elif i ==5:
                        temp='節後二周'
                    elif i ==6:
                        temp='節後三周'
                    elif i ==7:
                        temp='節後四周'
                    elif i ==8:
                        temp='最近一日'
                    temp_list.append(str(y))
                    temp_list.append(temp)
                    columns.append(tuple(temp_list))
            else:
                for i in range(0,8):
                    temp_list=[]
                    if i ==0:
                        temp='節前四周'
                    elif i ==1:
                        temp='節前三周'
                    elif i ==2:
                        temp='節前二周'
                    elif i ==3:
                        temp='節前一周'
                    elif i ==4:
                        temp='節後一周'
                    elif i ==5:
                        temp='節後二周'
                    elif i ==6:
                        temp='節後三周'
                    elif i ==7:
                        temp='節後四周'
                    temp_list.append(str(y))
                    temp_list.append(temp)
                    columns.append(tuple(temp_list))

        df4 = pd.DataFrame(Row_list,columns=pd.MultiIndex.from_tuples(columns))

        for index, row in df4.iterrows():
            product_name = [k for k in list(self.product_dict.keys())][index]
            df4.loc[index,('農產品','產品名稱')] = product_name

        for index, row in df4.iterrows():
            df4.loc[index,('節後四周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節後四周')]/df4.loc[index,(str(self.roc_year-1), '節後四周')]*100-100
            df4.loc[index,('節後四周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節後四周')]-df4.loc[index,(str(self.roc_year-1), '節後四周')]
            df4.loc[index,('前五年簡單平均','節後四周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節後四周'),(str(self.roc_year-2), '節後四周'),(str(self.roc_year-3), '節後四周'),(str(self.roc_year-4), '節後四周'),(str(self.roc_year-5), '節後四周')]])
            # df4.loc[index,('前五年簡單平均','節後四周平均(元/公斤)')] = df4.loc[index,[(str(self.roc_year-1), '節後四周'),(str(self.roc_year-2), '節後四周'),(str(self.roc_year-3), '節後四周'),(str(self.roc_year-4), '節後四周'),(str(self.roc_year-5), '節後四周')]].mean(axis=0)

            df4.loc[index,('節後三周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節後三周')]/df4.loc[index,(str(self.roc_year-1), '節後三周')]*100-100
            df4.loc[index,('節後三周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節後三周')]-df4.loc[index,(str(self.roc_year-1), '節後三周')]
            df4.loc[index,('前五年簡單平均','節後三周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節後三周'),(str(self.roc_year-2), '節後三周'),(str(self.roc_year-3), '節後三周'),(str(self.roc_year-4), '節後三周'),(str(self.roc_year-5), '節後三周')]])

            df4.loc[index,('節後二周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節後二周')]/df4.loc[index,(str(self.roc_year-1), '節後二周')]*100-100
            df4.loc[index,('節後二周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節後二周')]-df4.loc[index,(str(self.roc_year-1), '節後二周')]
            df4.loc[index,('前五年簡單平均','節後二周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節後二周'),(str(self.roc_year-2), '節後二周'),(str(self.roc_year-3), '節後二周'),(str(self.roc_year-4), '節後二周'),(str(self.roc_year-5), '節後二周')]])

            df4.loc[index,('節後一周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節後一周')]/df4.loc[index,(str(self.roc_year-1), '節後一周')]*100-100
            df4.loc[index,('節後一周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節後一周')]-df4.loc[index,(str(self.roc_year-1), '節後一周')]
            df4.loc[index,('前五年簡單平均','節後一周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節後一周'),(str(self.roc_year-2), '節後一周'),(str(self.roc_year-3), '節後一周'),(str(self.roc_year-4), '節後一周'),(str(self.roc_year-5), '節後一周')]])

            df4.loc[index,('節前一周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節前一周')]/df4.loc[index,(str(self.roc_year-1), '節前一周')]*100-100
            df4.loc[index,('節前一周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節前一周')]-df4.loc[index,(str(self.roc_year-1), '節前一周')]
            df4.loc[index,('前五年簡單平均','節前一周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節前一周'),(str(self.roc_year-2), '節前一周'),(str(self.roc_year-3), '節前一周'),(str(self.roc_year-4), '節前一周'),(str(self.roc_year-5), '節前一周')]])

            df4.loc[index,('節前二周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節前二周')]/df4.loc[index,(str(self.roc_year-1), '節前二周')]*100-100
            df4.loc[index,('節前二周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節前二周')]-df4.loc[index,(str(self.roc_year-1), '節前二周')]
            df4.loc[index,('前五年簡單平均','節前二周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節前二周'),(str(self.roc_year-2), '節前二周'),(str(self.roc_year-3), '節前二周'),(str(self.roc_year-4), '節前二周'),(str(self.roc_year-5), '節前二周')]])

            df4.loc[index,('節前三周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節前三周')]/df4.loc[index,(str(self.roc_year-1), '節前三周')]*100-100
            df4.loc[index,('節前三周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節前三周')]-df4.loc[index,(str(self.roc_year-1), '節前三周')]
            df4.loc[index,('前五年簡單平均','節前三周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節前三周'),(str(self.roc_year-2), '節前三周'),(str(self.roc_year-3), '節前三周'),(str(self.roc_year-4), '節前三周'),(str(self.roc_year-5), '節前三周')]])

            df4.loc[index,('節前四周與去年同期比較','漲跌率(%)')] = df4.loc[index,(str(self.roc_year), '節前四周')]/df4.loc[index,(str(self.roc_year-1), '節前四周')]*100-100
            df4.loc[index,('節前四周與去年同期比較','差幅(元/公斤)')] = df4.loc[index,(str(self.roc_year), '節前四周')]-df4.loc[index,(str(self.roc_year-1), '節前四周')]
            df4.loc[index,('前五年簡單平均','節前四周平均(元/公斤)')] = self.trimmean(df4.loc[index,[(str(self.roc_year-1), '節前四周'),(str(self.roc_year-2), '節前四周'),(str(self.roc_year-3), '節前四周'),(str(self.roc_year-4), '節前四周'),(str(self.roc_year-5), '節前四周')]])

        df4.index = df4.index + 1
        columns_list=[]
        columns_list.append(('農產品','產品名稱'))
        columns_list.append(('{}'.format(self.roc_year),'最近一日'))
        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節後四周'))
        columns_list.append(('節後四周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節後四周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節後四周平均(元/公斤)'))

        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節後三周'))
        columns_list.append(('節後三周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節後三周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節後三周平均(元/公斤)'))

        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節後二周'))
        columns_list.append(('節後二周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節後二周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節後二周平均(元/公斤)'))

        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節後一周'))
        columns_list.append(('節後一周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節後一周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節後一周平均(元/公斤)'))

        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節前一周'))
        columns_list.append(('節前一周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節前一周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節前一周平均(元/公斤)'))

        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節前二周'))
        columns_list.append(('節前二周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節前二周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節前二周平均(元/公斤)'))

        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節前三周'))
        columns_list.append(('節前三周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節前三周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節前三周平均(元/公斤)'))

        for y in range(self.roc_year,self.roc_year-5-1,-1):
            columns_list.append(('{}'.format(y), '節前四周'))
        columns_list.append(('節前四周與去年同期比較', '漲跌率(%)'))
        columns_list.append(('節前四周與去年同期比較', '差幅(元/公斤)'))
        columns_list.append(('前五年簡單平均', '節前四周平均(元/公斤)'))

        df4=df4[columns_list]

        df5 = df4.copy()
        if festival ==1:
            self.roc_date_range = self.ROC_Chinese_New_Year_dict
        if festival ==2:
            self.roc_date_range = self.ROC_Dragon_Boat_Festival_dict
        if festival ==3:
            self.roc_date_range = self.ROC_Mid_Autumn_Festival_dict

        #組合新欄位名稱
        yes_date=self.roc_date_range[str(self.roc_year)][-1].split('~')[0]
        if len(yes_date) > 5:
            yes_date = yes_date.split('/')[1]+'/'+yes_date.split('/')[2]
        columns_name = []
        columns_name.append('農產品')
        columns_name.append('最近一日\n{}/{}\n(元/公斤)'.format(self.today.year-1911,yes_date))
        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][7]
            columns_name.append('{0}年節後四周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節後四周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節後四周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節後四周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][6]
            columns_name.append('{0}年節後三周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節後三周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節後三周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節後三周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][5]
            columns_name.append('{0}年節後二周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節後二周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節後二周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節後二周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][4]
            columns_name.append('{0}年節後一周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節後一周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節後一周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節後一周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][3]
            columns_name.append('{0}年節前一周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節前一周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節前一周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節前一周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][2]
            columns_name.append('{0}年節前二周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節前二周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節前二周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節前二周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][1]
            columns_name.append('{0}年節前三周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節前三周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節前三周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節前三周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        for y in range(self.roc_year,self.roc_year-6,-1):
            date=self.roc_date_range[str(y)][0]
            columns_name.append('{0}年節前四周\n{1}\n(元/公斤)'.format(y,date))
        columns_name.append('{}年節前四周較{}年同期\n漲跌率\n(%)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('{}年節前四三周較{}年同期\n差幅\n(元/公斤)'.format(self.roc_year,self.roc_year-1))
        columns_name.append('近5年簡單平均\n({}-{}年)\n節前四周\n(元/公斤)'.format(self.roc_year-5,self.roc_year-1))

        df5.columns = columns_name

        if self.festival ==1:
            festival_title = '春節'
        if self.festival ==2:
            festival_title = '端午節'
        if self.festival ==3:
            festival_title = '中秋節'

        file_name = '{}_{}節前價格表.xlsx'.format(self.roc_year,festival_title)

        writer = pd.ExcelWriter(file_name)
        wb = openpyxl.Workbook()
        df6 = df5.copy()
        df6.to_excel(writer)
        ws = wb.create_sheet(index=0, title="價格表")

        #pandas to openpyxl
        for r in dataframe_to_rows(df6, index=False, header=False):
            ws.append(r)

        #設定字形大小及格式
        title_font = Font(size=22)
        content_font = Font(size=16)
        alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)

        #新增框線
        border = Border(top=Side(border_style='thin',color='000000'),
                        bottom=Side(border_style='thin', color='000000'),
                        left=Side(border_style='thin', color='000000'),
                        right=Side(border_style='thin', color='000000'))
        for _row in ws.iter_rows():
            for _cell in _row:
                _cell.border = border
                _cell.font = content_font
                _cell.number_format = '#,##0.0' #小數一位

        #在第一行前插入一行
        ws.insert_rows(1)
        # 合併儲存格
        ws.merge_cells('A1:BV1')
        #儲存格內容及格式
        ws['A1']='{}節前農產品價格變動情形表'.format(festival_title)
        ws['A1'].alignment=Alignment(horizontal='center', vertical='center')
        ws['A1'].font = title_font

        #插入兩行製作各欄位標題
        ws.insert_rows(2)
        ws.insert_rows(2)
        for i in range(1,len(df6.columns)+1):
            if i in [9,10,18,19,27,28,36,37,45,46,54,55,63,64,72,73]:
                ws.cell(row=2, column=i).value=df6.columns[i-1].split('\n')[0]
                ws.cell(row=3, column=i).value=df6.columns[i-1].split('\n')[1]+'\n'+df6.columns[i-1].split('\n')[2]
            else:
                ws.cell(row=2, column=i).value=df6.columns[i-1]
            ws.cell(row=2, column=i).font=content_font
            ws.cell(row=3, column=i).font=content_font
            

        # 合併儲存格
        for i in range(65,91):
            if i in (73,74,82,83):
                continue
            ws.merge_cells('{0}2:{0}3'.format(chr(i)))
        for i in range(65,91):
            if i in (65,66,74,75,83,84):
                continue
            ws.merge_cells('A{0}2:A{0}3'.format(chr(i)))
        for i in range(65,91):
            if i in (66,67,75,76,84,85):
                continue
            ws.merge_cells('B{0}2:B{0}3'.format(chr(i)))
        ws.merge_cells('I2:J2')
        ws.merge_cells('R2:S2')
        ws.merge_cells('AA2:AB2')
        ws.merge_cells('AJ2:AK2')
        ws.merge_cells('AS2:AT2')
        ws.merge_cells('BB2:BC2')
        ws.merge_cells('BK2:BL2')
        ws.merge_cells('BT2:BU2')

        # 設定儲存格格式
        for i in range(1,len(df6.columns)+1):
            ws.cell(row=2, column=i).alignment=alignment    #置中及換行
            ws.cell(row=3, column=i).alignment=alignment
            ws.cell(row=2, column=i).border=border  #框線
            ws.cell(row=3, column=i).border=border

        #欄位寬度
        ws.column_dimensions['A'].width = 33
        for c in range(2,len(df6.columns)+1):
            ws.column_dimensions[get_column_letter(c)].width = 22
        for _col in ['I','J','R', 'S','AA','AB','AJ','AK','AS','AT','BB','BC','BK','BL','BT','BU']:
            ws.column_dimensions[_col].width = 18.5

        #設定第2列高度
        ws.row_dimensions[2].height =42

        #隱藏欄位
        # hidden_columns=['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO']
        # for col in hidden_columns:
        #     ws.column_dimensions[col].hidden= True

        #凍結窗格
        ws.freeze_panes = ws['B4']

        # Close the Pandas Excel writer and output the Excel file.
        wb.save(file_name)
        return file_name

    def __call__(self, output_dir=settings.BASE_DIR):
        #產生節日日期區間
        self.festival_date(self.year, self.festival)

        #獲取完整交易表
        self.table = self.get_table()

        for i in self.pid:
            product_id_list = []
            source_id_list = []
            for j in i.product_id.all():
                product_id_list.append(j.id)

            for k in i.source.all():
                source_id_list.append(k.id)

            self.result_data = self.result(self.festival, product_id_list, source_id_list)

        #各品項逐一查詢價格
        # for k,v in self.product_dict.items():
            # self.result_data = self.get_data(self.festival,v)
        
        #只查詢單一日期,返回各品項查詢值
        if self.oneday:
            return self.result_data
        #產生八週周期日報,返回日報名稱
        else:
            file_name = self.data2pandas2save(self.festival, self.product_dict, self.result_data)
            file_path = Path(output_dir, file_name)
        return file_name,file_path


if __name__ == '__main__':
    start_time = time.time()
    rocyear = '109'
    festival = 3 #1:春節;2:端午節;3:中秋節
    oneday = False
    special_day = '2020-09-01'
    file_name = FestivalReportFactory(rocyear, festival,oneday=oneday, special_day=special_day)()
    if oneday:
        print('result =',file_name)
    else:
        print('{} save'.format(file_name))
    end_time = time.time()
    print('use time =',end_time-start_time)