import logging
import traceback


class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from .models import Log, LogType

        trace = None

        if record.exc_info:
            trace = traceback.format_exc()

        type_code = record.__dict__.get('type_code')
        msg = record.getMessage()
        logger_type = LogType.objects.filter(code=type_code).first()

        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': msg,
            'type': logger_type,
            'trace': trace
        }
        logging.debug(msg)
        Log.objects.create(**kwargs)
