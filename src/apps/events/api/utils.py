import pandas as pd


def funcBatchEventFile(file):
    data = pd.read_excel(file)
    res = pd.DataFrame()
    res['date'] = data['日期']
    res['types'] = data['事件分類']
    res['name'] = data['名稱']
    res['context'] = data['內容']

    return res.to_dict(orient='records')
