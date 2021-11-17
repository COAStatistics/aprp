from apps.dailytrans.builders.feed import Api
from apps.dailytrans.builders.utils import (
    director,
    date_generator,
    DirectData,
    date_delta,
)
from .models import Feed
import pandas as pd
import numpy as np
# from datetime import datetime,timedelta,date
import time
import os
import requests
import re
from bs4 import BeautifulSoup as bs
import json
import pytesseract
from PIL import Image
from django.conf import settings
import logging
db_logger = logging.getLogger('aprp')

MODELS = [Feed]
CONFIG_CODE = 'COG15'
LOGGER_TYPE_CODE = 'LOT-feed'

DELTA_DAYS = 1


@director
def direct(start_date=None, end_date=None, *args, **kwargs):

    data = DirectData(CONFIG_CODE, 2, LOGGER_TYPE_CODE)

    login_fail_flag = False

    for model in MODELS:
        api = Api(model=model, **data._asdict())

        #畜產會飼料價格為一整個月份的數據,飼料(玉米粒,黃豆粉), 因此爬取網頁數據後組合成 json 格式以便後續流程
        data_list = []

        #pytesseract執行檔絕對路徑,系統需要額外安裝 tesseract-ocr
        pytesseract.pytesseract.tesseract_cmd = settings.PYTESSERACT_PATH

        headers = {'User-Agent': settings.USER_AGENT,}

        #類型轉換,字符串轉浮點數,並將單一儲存格內如有多組數字時先行平均
        def str2float(l):
            sum = 0
            count = 0
            pattern = re.compile(r'\d+.?\d*\(.*?\)|\d+.?\d*')
            pattern2 = re.compile(r'\d+.?\d*')
            templ = pattern.findall(l)
            for j in templ:
                if "阿根廷" in j:
                    continue    #阿根廷的玉米粒報價較低是因為阿根廷的玉米粒較硬,不適合當豬的飼料,所以統計時要排除阿根廷的玉米粒報價
                else:
                    tempd=pattern2.findall(j)
                    try:
                        j = float(tempd[0])
                    except ValueError:
                        continue
                    sum = sum + j
                    count += 1
            if count:
                return round(sum / count, 2)
        
        #兩個來源地價格平均
        def float2avg(d1,d2):
            sum = 0
            count = 0
            if d1:
                sum = sum + d1
                count += 1
            if d2:
                sum = sum + d2
                count += 1
            if count:
                return round(sum / count, 2)

        #中央畜產會會員登入頁面
        naif_login_url = settings.DAILYTRAN_BUILDER_API['feed']
        ss = requests.Session()
        r1 = ss.get(naif_login_url, headers=headers)

        #儲存驗證碼圖片
        r2 = ss.get('https://www.naif.org.tw/libs/numToPic.aspx', headers=headers)
        with open('captcha.jpg', 'wb') as f:
            for chunk in r2:
                f.write(chunk)
        
        #OCR自動識別驗證碼
        captcha = Image.open('captcha.jpg')
        code = pytesseract.image_to_string(captcha).strip()
        if len(code) > 4:
            code = code[:4]

        #登入會員系統
        post_url = 'https://www.naif.org.tw/memberLogin.aspx'

        postdata = {
        'url': '/memberLogin.aspx',
        'myAccount': settings.NAIF_ACCOUNT,
        'myPassword': settings.NAIF_PASSWORD,
        'code': code,
        'btnSend': '登入會員',
        'frontTitleMenuID': 105,
        'frontMenuID': 148,
        }

        r3 = ss.post(post_url, headers=headers, data=postdata)

        if start_date:
            start_year = start_date.year
            start_month = start_date.month
        if end_date:
            end_year = end_date.year
            end_month = end_date.month

        if not start_date and not end_date:
            delta_start_date, delta_end_date = date_delta(DELTA_DAYS)
            start_year = delta_start_date.year
            start_month = delta_start_date.month
            end_year = delta_end_date.year
            end_month = delta_end_date.month

    #         response = api.request(date=delta_start_date)
    #         api.load(response)         

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

                #飼料價格頁面
                r4 = ss.get(f'https://www.naif.org.tw/infoFeed.aspx?sYear={y}&sMonth={m}&btnSearch=%E6%90%9C%E5%B0%8B&frontMenuID=118&frontTitleMenuID=37', headers=headers)
                soup = bs(r4.text, 'html.parser')
                table = soup.find('table', {'cellspacing': '1'})
                alert = soup.find('script').string

                #登入失敗
                if alert and '請先登入會員!!' in alert:
                    db_logger.warning(f'Login failed for naif, captcha : {code}',extra={
                                                                                            'logger_type': data.logger_type_code,
                                                                                        })
                    login_fail_flag = True
                    break

                #登入成功
                if not alert and table:
                    trs = table.find_all('tr')[4:]
                    for tr in trs:

                        #組合json格式用預設格式的
                        default_dict1 = {
                                            "date": "",
                                            "item": "玉米粒",
                                            "price": 0,
                                            "priceUnit": "元/公斤"
                                        }
                        default_dict2 = {
                                            "date": "",
                                            "item": "黃豆粉",
                                            "price": 0,
                                            "priceUnit": "元/公斤"
                                        }

                        temp_list = []
                        d = tr.find('th').getText() #日期欄位
                        tds = tr.find_all('td')
                        #葉科詢問畜產會得知中華食物網為上游的港口數據,養豬合作社為下游單位,當缺料時養豬合作社就會無法報價
                        #因此飼料數據來源由養豬合作社改為中華食物網
                        for td in tds[6:10]:
                            temp_list.append(td.getText())

                        #玉米粒-中華食物網:台中港
                        d1 = str2float(temp_list[0]) 
                        #玉米粒-中華食物網:高雄港
                        d2 = str2float(temp_list[1])
                        #黃豆粉-中華食物網:台中港
                        d3 = str2float(temp_list[2])
                        #黃豆粉-中華食物網:高雄港
                        d4 = str2float(temp_list[3])
                        
                        #玉米粒來源地平均
                        avg1 = float2avg(d1,d2)
                        #黃豆粉來源地平均
                        avg2 = float2avg(d3,d4)

                        #組合成API可用的格式
                        if avg1:
                            default_dict1['date'] = f'{y}/{m}/{d}'
                            default_dict1['price'] = avg1
                            data_list.append(default_dict1)

                        if avg2:
                            default_dict2['date'] = f'{y}/{m}/{d}'
                            default_dict2['price'] = avg2
                            data_list.append(default_dict2)

                time.sleep(5)

            #登入失敗時離開
            else:
                continue
            break

        if not login_fail_flag:
            api.load(json.dumps(data_list))

            #刪除驗證碼圖片檔案    
            os.remove('captcha.jpg')

    return data