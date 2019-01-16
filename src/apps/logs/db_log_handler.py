import logging
import traceback


class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from .models import Log, LogType

        trace = None

        if record.exc_info:
            trace = traceback.format_exc()

        type_code = record.__dict__.get('type_code')
        request_url = record.__dict__.get('request_url')
        duration = record.__dict__.get('duration')

        msg = record.getMessage()
        logger_type = LogType.objects.filter(code=type_code).first()

        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': msg,
            'trace': trace,
            'type': logger_type,
            'url': request_url,
            'duration': duration,
        }
        logging.debug(msg)
        Log.objects.create(**kwargs)
