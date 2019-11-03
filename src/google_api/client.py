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
    def load_from_env(cls, env_prefix):
        keys_env_variables_map = {
            key: env_prefix + key.upper() for key in
            list(cls._OAUTH2_INSTALLED_APP_KEYS)
        }
        config_data = {
            key: os.environ[env_variable]
            for key, env_variable in keys_env_variables_map.items()
            if env_variable in os.environ
        }
        kwargs = cls._get_client_kwargs(config_data)
        return cls(**kwargs)
