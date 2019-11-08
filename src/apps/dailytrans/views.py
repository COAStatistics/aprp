import os
from datetime import datetime, timedelta
from django.shortcuts import render

from google_api.google_drive.client import GoogleDriveClient
from apps.dailytrans.models import DailyReport
from apps.dailytrans.reports.dailyreport import DailyReportFactory


def render_daily_report(request):
    folder_id = '1HMW-KtLHPhH0DDQ9vSU5bIfgre5qhfFk'
    google_drive_client = GoogleDriveClient.load_from_env(env_prefix='GOOGLE_DRIVE_')

    data = request.GET or request.POST

    day = data.get('day')
    month = data.get('month')
    year = data.get('year')

    if not all([day, month, year]):
        yesterday = datetime.today() - timedelta(days=-1)
        day, month, year = yesterday.day, yesterday.month, yesterday.year

    daily_report = DailyReport.objects.filter(date__year=year, date__month=month, date__day=day).first()
    if daily_report:
        file_id = daily_report.file_id
    else:
        date = datetime(int(year), int(month), int(day))
        # generate file
        factory = DailyReportFactory(specify_day=date)
        file_name, file_path = factory()
        # upload file
        response = google_drive_client.media_upload(
            name=file_name,
            file_path=file_path,
            from_mimetype=google_drive_client.XLSX_MIME_TYPE,
            parents=[folder_id],
        )
        file_id = response.get('id')
        # make public
        google_drive_client.set_public_permission(file_id)
        # write result to database
        DailyReport.objects.create(date=date, file_id=file_id)
        # remove local file
        os.remove(file_path)

    context = {
        'file_id': file_id
    }
    template = 'daily-report-iframe.html'

    return render(request, template, context)
