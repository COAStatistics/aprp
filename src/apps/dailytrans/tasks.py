import os
import logging
from datetime import datetime, timedelta
from celery.task import task
from django.conf import settings

from apps.dailytrans.models import DailyTran, DailyReport
from apps.dailytrans.reports.dailyreport import DailyReportFactory
from google_api.backends import DefaultGoogleDriveClient


@task(name="DeleteNotUpdatedTrans")
def delete_not_updated_trans(not_updated_times=15):
    pass
    # db_logger = logging.getLogger('aprp')
    # logger_extra = {
    #     'type_code': 'LOT-dailytrans',
    # }
    # try:
    #     dailytrans = DailyTran.objects.filter(not_updated__gte=not_updated_times)
    #     count = dailytrans.count()
    #     dailytrans.all().delete()
    #     if count > 0:
    #         db_logger.info('Delete %s not updated dailytrans' % count, extra=logger_extra)

    # except Exception as e:
    #     db_logger.exception(e, extra=logger_extra)


@task(name='UpdateDailyReport')
def update_daily_report(delta_days=-1):
    db_logger = logging.getLogger('aprp')
    logger_extra = {
        'type_code': 'LOT-dailytrans',
    }
    folder_id = settings.DAILY_REPORT_FOLDER_ID
    google_drive_client = DefaultGoogleDriveClient()

    date = datetime.today() + timedelta(days=delta_days)

    # generate file
    try:
        factory = DailyReportFactory(specify_day=date)
        file_name, file_path = factory()
    except Exception as e:
        db_logger.exception(e, extra=logger_extra)
        
        return

    daily_report = DailyReport.objects.filter(date=date).first()
    if not daily_report:
        # upload file
        response = google_drive_client.media_upload(
            name=file_name,
            file_path=file_path,
            from_mimetype=google_drive_client.XLSX_MIME_TYPE,
            parents=[folder_id],
        )
        file_id = response.get('id')
        google_drive_client.set_public_permission(file_id)
        # write result to database
        DailyReport.objects.create(date=date, file_id=file_id)
    else:
        google_drive_client.media_update(
            file_id=daily_report.file_id,
            file_path=file_path,
            from_mimetype=google_drive_client.XLSX_MIME_TYPE
        )
        daily_report.update_time = datetime.now()
        daily_report.save()

    # remove local file
    os.remove(file_path)
