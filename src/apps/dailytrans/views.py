import os
from datetime import datetime, timedelta
from django.shortcuts import render
from django.conf import settings

from google_api.backends import DefaultGoogleDriveClient
from apps.dailytrans.models import DailyReport, FestivalReport
from apps.dailytrans.reports.dailyreport import DailyReportFactory
from apps.dailytrans.reports.festivalreport import FestivalReportFactory
from distutils.util import strtobool
import logging
from apps.configs.models import Festival, FestivalItems
# import time

def upload_file2google_client(file_name, file_path, folder_id, from_mimetype='XLSX'):
    google_drive_client = DefaultGoogleDriveClient()
    if from_mimetype=='XLSX':
        from_mimetype=google_drive_client.XLSX_MIME_TYPE
    response = google_drive_client.media_upload(
        name=file_name,
        file_path=file_path,
        from_mimetype=from_mimetype,
        parents=[folder_id],
    )
    file_id = response.get('id')
    google_drive_client.set_public_permission(file_id)
    return file_id

def render_daily_report(request):
    folder_id = settings.DAILY_REPORT_FOLDER_ID
    google_drive_client = DefaultGoogleDriveClient()

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


def render_festival_report(request,refresh=False):
    context = {}
    folder_id = settings.FESTIVAL_REPORT_FOLDER_ID
    # google_drive_client = DefaultGoogleDriveClient()
    data = request.GET or request.POST
    festival_id = data.get('festival_id')
    festival = data.get('festival_name')
    roc_year=festival.split('_')[0]
    year = int(roc_year) + 1911
    festival_name = festival.split('_')[1]
    refresh = bool(strtobool(data.get('refresh')))
    oneday = bool(strtobool(data.get('oneday')))

    # start_time = time.time()
    if oneday:
        day = data.get('day')
        if len(day)==1:
            day = '0'+ day
        month = data.get('month')
        if len(month)==1:
            month = '0'+ month
        year = data.get('year')
        date = year + '-' + month + '-' + day
    
    #html switch to db
    if festival_name=='春節':
        festival=1
    elif festival_name=='端午節':
        festival=2
    elif festival_name=='中秋節':
        festival=3

    if oneday:
        factory = FestivalReportFactory(rocyear=roc_year,festival=festival,oneday=oneday,special_day=date)
        resule_data = factory()
        product_name_list = []
        pid = FestivalItems.objects.filter(festivalname__id__contains=festival)
        for i in pid.all():
            product_name_list.append(i)

        values_list = []
        for v in resule_data.values():
            if str(v[str(year)][0]) == 'nan':
                v[str(year)][0] = None
            values_list.append(v[str(year)][0])

        product_data={}
        if len(values_list) == len(product_name_list):
            for i in range(len(values_list)):
                product_data[product_name_list[i]]=values_list[i]

        context = {
                'oneday': oneday,
                'festival_name': festival_name,
                'date':date,
                'product_data': product_data,
            }

    else:
        festival_report = FestivalReport.objects.filter(festival_id_id=festival_id)

        if not refresh:
            if festival_report:
                file_id = festival_report[0].file_id
            else:
                # generate file
                factory = FestivalReportFactory(rocyear=roc_year,festival=festival)
                file_name, file_path = factory()
                # upload file
                file_id = upload_file2google_client(file_name, file_path, folder_id)
                # write result to database
                FestivalReport.objects.create(festival_id_id=festival_id, file_id=file_id)
                # remove local file
                os.remove(file_path)

        else:
            file_id = festival_report[0].file_id
            festival_report[0].delete()
            google_drive_client = DefaultGoogleDriveClient()
            response = google_drive_client.delete_file(file_id=file_id)
            if not response: #google drive 刪除成功返回空值
                pass
            else:
                db_logger = logging.getLogger('aprp')
                db_logger.warning(f'delete google file error:{response}', extra={'type_code': 'festivalreport'})
            # 重新產生報告
            factory = FestivalReportFactory(rocyear=roc_year,festival=festival)
            file_name, file_path = factory()
            file_id = upload_file2google_client(file_name, file_path, folder_id)
            FestivalReport.objects.create(festival_id_id=festival_id, file_id=file_id)
            os.remove(file_path)

        refresh = True
        context = {
            'file_id': file_id,
            'refresh' : refresh,
            'roc_year': roc_year,
            'festival_name': festival_name,
        }
    template = 'festival-report-iframe.html'
    # end_time = time.time()
    # print('spend time=',end_time-start_time)
    return render(request, template, context)