import abc
import logging
import time
import requests
from django.conf import settings
from apps.configs.models import (
    Source,
    Config,
)


class AbstractApi(object):
    _metaclass__ = abc.ABCMeta

    def __init__(self, model, config_code=None, type_id=None, logger=None, logger_type_code=None):
        if self.API_NAME is None:
            raise NotImplementedError('Class attribute API_NAME not advised at AbstractApi inheritance')

        if not settings.DAILYTRAN_BUILDER_API:
            raise NotImplementedError('Dictionary DAILYTRAN_BUILDER_API not advised in settings')

        try:
            self.API_URL = settings.DAILYTRAN_BUILDER_API[self.API_NAME]
        except KeyError:
            raise NotImplementedError('Can not find key for API name %s in DAILYTRAN_BUILDER_API' % self.API_NAME)

        if self.ZFILL is None:
            raise NotImplementedError('Class attribute ZFILL not advised at AbstractApi inheritance')

        if self.SEP is None:
            raise NotImplementedError('Class attribute SEP not advised at AbstractApi inheritance')

        if self.ROC_FORMAT is None:
            raise NotImplementedError('Class attribute ROC_FORMAT not advised at AbstractApi inheritance')

        if not isinstance(logger, str):
            raise NotImplementedError('Argument logger must be str')

        self.MODEL = model

        if config_code:
            self.CONFIG = Config.objects.filter(code=config_code).first()
            self.SOURCE_QS = Source.objects.filter(configs__exact=self.CONFIG)
            self.PRODUCT_QS = self.MODEL.objects


        if type_id:
            self.SOURCE_QS = self.SOURCE_QS.filter(type__id=type_id)
            self.PRODUCT_QS = self.PRODUCT_QS.filter(type__id=type_id, track_item=True)

        self.target_items = {obj[0] for obj in self.PRODUCT_QS.values_list('code')}
        self.LOGGER = logging.getLogger(logger)
        self.LOGGER_EXTRA = {
            'type_code': logger_type_code,
            'request_url': None,
        }

    @abc.abstractmethod
    def request(self, *args):
        return

    @abc.abstractmethod
    def hook(self, *args):
        return

    @abc.abstractmethod
    def load(self, response):
        return

    def get(self, url, *args, **kwargs):
        response = requests.Response()
        retry_count = 0
        while response.status_code != 200 and retry_count < 5:
            try:
                response = requests.get(url, *args, **kwargs)
                self.LOGGER_EXTRA['request_url'] = response.request.url
            except requests.exceptions.ConnectionError:
                response = requests.Response()

            if response.status_code != 200:
                retry_count += 1
                self.LOGGER.error('Connection Refused, Retry %s Time' % retry_count, extra=self.LOGGER_EXTRA)
                time.sleep(15)
                continue

        return response
