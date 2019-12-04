import os
from google.oauth2.credentials import Credentials as InstalledAppCredentials

_DEFAULT_TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'


class GoogleOAuthClient(object):
    _OAUTH2_INSTALLED_APP_KEYS = ('client_id', 'client_secret', 'refresh_token')

    def __init__(self, credentials):
        self.credentials = credentials

    @classmethod
    def _get_client_kwargs(cls, config_data):
        credentials = InstalledAppCredentials(token=None,
                                              client_id=config_data.get('client_id'),
                                              client_secret=config_data.get('client_secret'),
                                              refresh_token=config_data.get('refresh_token'),
                                              token_uri=_DEFAULT_TOKEN_URI)
        return {'credentials': credentials}

    @classmethod
    def _get_credentials(cls, client_id, client_secret, refresh_token):
        credentials = InstalledAppCredentials(token=None,
                                              client_id=client_id,
                                              client_secret=client_secret,
                                              refresh_token=refresh_token,
                                              token_uri=_DEFAULT_TOKEN_URI)
        return credentials

    @classmethod
    def load_from_dict(cls, config_dict):
        client_id = config_dict.pop('client_id')
        client_secret = config_dict.pop('client_secret')
        refresh_token = config_dict.pop('refresh_token')
        credentials = cls._get_credentials(client_id, client_secret, refresh_token)
        kwargs = {**config_dict, 'credentials': credentials}
        return cls(**kwargs)
