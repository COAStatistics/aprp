from django.db.models import Q
import datetime
import json
from .utils import date_transfer
from .abstract import AbstractApi
from apps.dailytrans.models import DailyTran

import pandas as pd
import numpy as np
import os
import time
import requests
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup as bs
from django.conf import settings

class Api(AbstractApi):

    # Settings
    API_NAME = 'naifchickens'
    ZFILL = True
    ROC_FORMAT = False
    SEP = '/'
    headers = {'User-Agent': settings.USER_AGENT,}

    def __init__(self, model, config_code, type_id, logger_type_code=None):
        super(Api, self).__init__(model=model, config_code=config_code, type_id=type_id,
                                  logger='aprp', logger_type_code=logger_type_code)

    def hook(self, dic):

        for key, value in dic.items():
            if isinstance(value, str):
                dic[key] = value.strip()

        product_code = dic.get('item')
        product = self.PRODUCT_QS.filter(code=product_code).first()

        if product:
            tran = DailyTran(
                product=product,
                avg_price=dic.get('price'),
                avg_weight=dic.get('weight'),
                volume=dic.get('volume'),
                date=date_transfer(sep=self.SEP, string=dic.get('date'), roc_format=self.ROC_FORMAT)
            )
            return tran
        else:
            if not product:
                self.LOGGER.warning('Cannot Match Product: "%s" In Dictionary %s'
                                    % (product_code, dic), extra=self.LOGGER_EXTRA)
            return dic

    def request(self, start_date=None, end_date=None, id=None, source=None, code=None, name=None):

        if id >= 150001 and id <= 150002:   #環南市場:環南-白肉雞/環南-土雞
            login_fail_flag = False
            #畜產會環南家禽批發市場交易行情表為一整個月份的數據,因此爬取網頁數據後組合成 json 格式以便後續流程
            data_list = []

            #pytesseract執行檔絕對路徑,系統需要額外安裝 tesseract-ocr
            pytesseract.pytesseract.tesseract_cmd = settings.PYTESSERACT_PATH

            #中央畜產會會員登入頁面
            naif_login_url = settings.DAILYTRAN_BUILDER_API['naifchickens']
            ss = requests.Session()
            r1 = ss.get(naif_login_url, headers=self.headers)

            #儲存驗證碼圖片
            r2 = ss.get('https://www.naif.org.tw/libs/numToPic.aspx', headers=self.headers)
            with open('captcha.jpg', 'wb') as f:
                for chunk in r2:
                    f.write(chunk)
            
            #OCR自動識別驗證碼
            captcha = Image.open('captcha.jpg')
            captcha_code = pytesseract.image_to_string(captcha).strip()
            if len(captcha_code) > 4:
                captcha_code = captcha_code[:4]

            #登入會員系統
            post_url = 'https://www.naif.org.tw/memberLogin.aspx'

            postdata = {
            'url': '/memberLogin.aspx',
            'myAccount': settings.NAIF_ACCOUNT,
            'myPassword': settings.NAIF_PASSWORD,
            'code': captcha_code,
            'btnSend': '登入會員',
            'frontTitleMenuID': 105,
            'frontMenuID': 148,
            }

            r3 = ss.post(post_url, headers=self.headers, data=postdata)

            if start_date:
                start_year = start_date.year
                start_month = start_date.month
            if end_date:
                end_year = end_date.year
                end_month = end_date.month

            chickens_dict = {
                        '120':'環南-白肉雞',
                        '137':'環南-土雞',
                    }   

            for k,v in chickens_dict.items():

                for y in range(start_year, end_year+1):
                    if y == start_year and y == end_year:
                        s_month = start_month
                        e_month = end_month
                    elif y == start_year:
                        s_month = start_month
                        e_month = 12
                    elif y == end_year:
                        s_month = 1
                        e_month = end_month
                    else:
                        s_month = 1
                        e_month = 12
                    for m in range(s_month, e_month+1):
                        if len(str(m)) == 1:
                            m = '0' + str(m)

                        #台北市環南家禽批發市場交易行情表頁面
                        if k == '120':  #環南-白肉雞
                            r4 = ss.get(f'https://www.naif.org.tw/infoWhiteChicken.aspx?sYear={y}&sMonth={m}&btnSearch=%E6%90%9C%E5%B0%8B&frontMenuID=120&frontTitleMenuID=37', headers=self.headers)
                        if k == '137':   #環南-土雞
                            r4 = ss.get(f'https://www.naif.org.tw/infoEndemicChicken.aspx?sYear={y}&sMonth={m}&btnSearch=%E6%90%9C%E5%B0%8B&frontMenuID=137&frontTitleMenuID=37', headers=self.headers)
                        soup = bs(r4.text, 'html.parser')
                        table = soup.find('table', {'cellspacing': '1'})
                        alert = soup.find('script').string

                        #登入失敗
                        if alert and '請先登入會員!!' in alert:
                            self.LOGGER.warning(f'Login failed for naif, captcha : {captcha_code}', extra=self.LOGGER_EXTRA)
                            login_fail_flag = True
                            break

                        #登入成功
                        if not alert and table:
                            trs = table.find_all('tr')[1:]
                            for tr in trs:

                                #組合json格式用預設格式的
                                default_dict1 = {
                                                    "date": "",
                                                    "item": v,
                                                    "price": 0,
                                                    "weight":0,
                                                    "volume":0,
                                                    "priceUnit": "元/公斤"
                                                }
                                
                                d = tr.find('th').getText()
                                tds = tr.find_all('td')

                                avg_price = tds[4].getText().replace(",","").strip()
                                volume = tds[6].getText().replace(",","").strip()
                                weight = tds[7].getText().replace(",","").strip()
                                if avg_price:
                                    try:
                                        avg_price = float(avg_price)
                                    except ValueError:
                                        self.LOGGER.warning(f'{y}/{m}/{d} {v} price Value Error : {tds[4].getText().replace(",","").strip()}', extra=self.LOGGER_EXTRA)
                                        avg_price = None

                                if volume:
                                    try:
                                        volume = float(volume)
                                    except ValueError:
                                        self.LOGGER.warning(f'{y}/{m}/{d} {v} volume Value Error : {tds[6].getText().replace(",","").strip()}', extra=self.LOGGER_EXTRA)
                                        volume = None

                                if weight:
                                    try:
                                        weight = float(weight)
                                    except ValueError:
                                        self.LOGGER.warning(f'{y}/{m}/{d} {v} weight Value Error : {tds[7].getText().replace(",","").strip()}', extra=self.LOGGER_EXTRA)
                                        weight = None

                                #組合成API可用的格式
                                if avg_price and volume and weight:
                                    default_dict1['date'] = f'{y}/{m}/{d}'
                                    default_dict1['price'] = avg_price
                                    default_dict1['volume'] = volume
                                    default_dict1['weight'] = weight
                                    data_list.append(default_dict1)

                        time.sleep(5)

                    #登入失敗時離開
                    else:
                        continue
                    break
            
            #刪除驗證碼圖片檔案    
            os.remove('captcha.jpg')

            return data_list

        elif id >= 150003 and id <= 150004: #家禽行情:白肉雞總貨/紅羽土雞總貨
            data_list = []
            # 將輸入的指定日期區間換成 list
            date_range = pd.Series(pd.date_range(start=start_date, end=end_date))
            for d in date_range:
                date = d.strftime('%Y-%m-%d')
            
                naif_url = 'https://ppg.naif.org.tw/naif/MarketInformation/Poultry/Product.aspx'
                not_data_flag = False   #判斷有無交易用的旗標

                postdata = {
                            '__VIEWSTATE:': None,
                            '__VIEWSTATEGENERATOR': None,
                            '__EVENTVALIDATION': None,
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$CheckBoxList_Market$6': '1',  # 肉品市場,台灣地區
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$CheckBoxList_Product$6': 'ON31',  # 白肉雞總貨
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$CheckBoxList_Product$8': 'ON41',  # 紅羽土雞雞總貨
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$TextBox_Content1_ThisDate': date,    # 日行情比較,本期
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$TextBox_Content1_LastDate': date,    # 日行情比較,上期
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$Button_Content1_Submit': '查詢',
                            #
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content2_ThisDate_Year': '2022',    # 旬行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content2_ThisDate_Month': '1',  # 旬行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content2_ThisDate_TenDays': '1',    # 旬行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content2_LastDate_Year': '2022',    # 旬行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content2_LastDate_Month': '1',  # 旬行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content2_LastDate_TenDays': '1',    # 旬行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content3_ThisDate_Year': '2022',    # 月行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content3_ThisDate_Month': '1',  # 月行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content3_LastDate_Year': '2022',    # 月行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content3_LastDate_Month': '1',  # 月行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content4_ThisDate_Year': '2022',    # 年行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$DropDownList_Content4_LastDate_Year': '2022',    # 年行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$TextBox_Content5_ThisDate_BegDate': '2022-01-20',    # 指定期間行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$TextBox_Content5_ThisDate_EndDate': '2022-01-26',    # 指定期間行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$TextBox_Content5_LastDate_BegDate': '2022-01-20',    # 指定期間行情比較
                            'ctl00$ctl00$ContentPlaceHolder_contant$ContentPlaceHolder_contant$TextBox_Content5_LastDate_EndDate': '2022-01-26'    # 指定期間行情比較
                            }

                # 組合json格式用預設格式
                dict1 = {
                        "date": "",
                        "item": "白肉雞總貨",
                        "price": 0,        
                        "volume":0,
                        "weight":0,
                        "priceUnit": "元/公斤"
                        }
                dict2 = {
                        "date": "",
                        "item": "紅羽土雞總貨",
                        "price": 0,        
                        "volume":0,
                        "weight":0,
                        "priceUnit": "元/公斤"
                        }
                
                ss = requests.Session()
                r3 = ss.get(naif_url, headers=self.headers)
                soup = bs(r3.text, 'html.parser')

                postdata['__VIEWSTATE'] = soup.find(id='__VIEWSTATE').attrs['value']
                postdata['__VIEWSTATEGENERATOR'] = soup.find(id='__VIEWSTATEGENERATOR').attrs['value']
                postdata['__EVENTVALIDATION'] = soup.find(id='__EVENTVALIDATION').attrs['value']

                r4 = ss.post(naif_url, headers=self.headers, data=postdata)
                soup2 = bs(r4.text, 'html.parser')

                table = soup2.find('table', {'cellspacing': '0'})
                not_data_msg = table.find_all('tr')[3].getText().strip()   # 特殊日期沒有交易會顯示"查無交易資料!"
                if '查無交易資料！' in not_data_msg:
                    self.LOGGER.warning(f'{date} 查無交易資料！', extra=self.LOGGER_EXTRA)
                    not_data_flag = True
                    continue

                trs = table.find_all('tr')[5:7]
                if not not_data_flag:
                    for tr in trs:
                        tds = tr.find_all('td')
                        name = tds[0].getText() + tds[1].getText()  #將"白肉雞"/"紅羽土雞"和"總貨"字串連接
                        this_avg_price = tds[2].getText()
                        # last_avg_price = tds[3].getText()
                        this_volume = tds[5].getText()
                        # last_volume = tds[6].getText()
                        this_weight = tds[8].getText()
                        # last_weight = tds[9].getText()

                        #如果當天沒有數據
                        if this_avg_price == '-':
                            self.LOGGER.warning(f'{date} {name} 無交易數據', extra=self.LOGGER_EXTRA)
                            continue

                        # 白肉雞總貨和紅羽土雞總貨數據在同一頁面,判斷品項分開存資料
                        if name in dict1['item']:
                            dict1['date'] = date.replace('-','/')
                            dict1['price'] = float(this_avg_price)
                            dict1['volume'] = float(this_volume)
                            dict1['weight'] = float(this_weight)
                            data_list.append(dict1)
                        if name in dict2['item']:
                            dict2['date'] = date.replace('-','/')
                            dict2['price'] = float(this_avg_price)
                            dict2['volume'] = float(this_volume)
                            dict2['weight'] = float(this_weight)
                            data_list.append(dict2)

                time.sleep(3)      

            return data_list

    def load(self, response):
        data = []
        # if response.text:
        #     data = json.loads(response.text, object_hook=self.hook)
        if response:
            data = json.loads(response, object_hook=self.hook)

        # data should look like [D, B, {}, C, {}...] after loads
        for obj in data:
            if isinstance(obj, DailyTran):
                try:
                    # update if exists
                    daily_tran_qs = DailyTran.objects.filter(Q(date__exact=obj.date)
                                                             & Q(product=obj.product))

                    if daily_tran_qs.count() > 1:
                        # log as duplicate
                        items = str(daily_tran_qs.values_list('id', flat=True))

                        self.LOGGER.warning('Find duplicate DailyTran item: %s' % items, extra=self.LOGGER_EXTRA)

                    elif daily_tran_qs.count() == 1:
                        daily_tran_qs.update(avg_price=obj.avg_price)
                    else:
                        if obj.avg_price > 0:
                            obj.save()

                except Exception as e:
                    self.LOGGER.exception(e, extra=self.LOGGER_EXTRA)
