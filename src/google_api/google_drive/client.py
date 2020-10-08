import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from google_api.client import GoogleOAuthClient

logger = logging.getLogger(__name__)


class GoogleDriveClient(GoogleOAuthClient):
    XLSX_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    FILE_MIME_TYPE = 'application/vnd.google-apps.file'
    SPREAD_SHEET_MIME_TYPE = 'application/vnd.google-apps.spreadsheet'
    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)

    def media_upload(self, name, file_path, from_mimetype, to_mimetype=None, parents=[], fields='id'):
        file_metadata = {
            'name': name,
            'parents': parents,
        }
        if to_mimetype:
            file_metadata['mimeType'] = to_mimetype
        media = MediaFileUpload(file_path,
                                mimetype=from_mimetype,
                                resumable=False)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields=fields)
        return file.execute()

    def media_update(self, file_id, file_path, from_mimetype, to_mimetype=None):
        file_metadata = {}
        if to_mimetype:
            file_metadata['mimeType'] = to_mimetype
        media = MediaFileUpload(file_path,
                                mimetype=from_mimetype,
                                resumable=False)
        file = self.service.files().update(fileId=file_id,
                                           body=file_metadata,
                                           media_body=media)
        return file.execute()

    def set_domain_permission(self, file_id, domain='localhost', role='reader'):
        permission_metadata = {
            'role': role,
            'type': 'domain',
            'domain': domain,
        }
        permission = self.service.permissions().create(fileId=file_id, body=permission_metadata)
        return permission.execute()

    def set_public_permission(self, file_id, role='reader'):
        permission_metadata = {
            'role': role,
            'type': 'anyone',
        }
        permission = self.service.permissions().create(fileId=file_id, body=permission_metadata)
        return permission.execute()

    def search_by_name(self, name, mimetype, search_fields=['id']):
        q = f"mimeType='{mimetype}' AND name='{name}'"
        fields = f"files({', '.join(search_fields)})"

        response = self.service.files().list(q=q, spaces='drive', fields=fields).execute()
        return response.get('files', None)

    def get_revision(self, file_id, revision_id, fields='*'):
        return self.service.revisions().get(fileId=file_id, revisionId=revision_id, fields=fields).execute()

    def delete_file(self, file_id):
        file = self.service.files().delete(fileId=file_id)
        return file.execute()