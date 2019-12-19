import pandas as pd


def convert_date(date):
    date = date.split('/')
    year = int(date[0])
    month = str(int(date[1])).zfill(2)
    day = str(int(date[-1])).zfill(2)
    if year < 1911:
        year += 1911
    return '{}/{}/{}'.format(year, month, day)


def funcBatchEventFile(file):
    res = pd.read_excel(file)
    res.columns = ['date', 'types', 'name', 'context']
    res['date'] = res['date'].apply(convert_date)

    return res.to_dict(orient='records')
