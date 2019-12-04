from django.conf import settings
from google_api.google_drive.client import GoogleDriveClient


class DefaultGoogleDriveClient(object):
    """A singleton class for accessing system user's google drive resource by giving a pre-generated refresh token"""
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = GoogleDriveClient.load_from_dict({
                'client_id': settings.GOOGLE_DRIVE_CLIENT_ID,
                'client_secret': settings.GOOGLE_DRIVE_CLIENT_SECRET,
                'refresh_token': settings.GOOGLE_DRIVE_REFRESH_TOKEN,
            })
        return cls._instance
