from datetime import datetime, timedelta
from django.shortcuts import render


def render_daily_report(request):

    data = request.GET or request.POST

    day = data.get('day')
    month = data.get('month')
    year = data.get('year')

    if not all([day, month, year]):
        yesterday = datetime.today() - timedelta(days=-1)
        day, month, year = yesterday.day, yesterday.month, yesterday.year

    print(day, month, year)

    context = {
        'file_id': '10ub0-gLH12GtSKeZfy8cAtQzN_SI9ktJ'
    }
    template = 'daily-report-iframe.html'

    return render(request, template, context)
