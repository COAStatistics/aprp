import pandas as pd


def convert_date(date):
    try:
        date = date.split('/')
    except:
        #日期格式錯誤無法轉換
        return None

    year = int(date[0])
    month = str(int(date[1])).zfill(2)
    day = str(int(date[-1])).zfill(2)
    if year < 1911:
        year += 1911
    return '{}/{}/{}'.format(year, month, day)


def funcBatchEventFile(file):
    #如果日期格式正確,但該事件不在事件分類內,會出現上傳成功但有錯誤筆數
    try:
        res = pd.read_excel(file)
        res.columns = ['date', 'types', 'name', 'context']
        res['date'] = res['date'].apply(convert_date)

        #日期格式錯誤無法轉換
        if res['date'].values[0] is None:
            return None
        
        #格式正確
        return res.to_dict(orient='records')

    except:
        #檔案非excel
        #檔案內只有1列為標題,而沒有內容
        #檔案內欄位數量錯誤
        #檔案內有多列,但其中一列日期格式錯誤
        return None

