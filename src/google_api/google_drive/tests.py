import pytest
from django.test import SimpleTestCase
from django.conf import settings

from .client import GoogleDriveClient


@pytest.mark.secret
@pytest.mark.google_api
class GoogleDriveClientTestCase(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_folder_id = settings.TEST_DAILY_REPORT_FOLDER_ID
        cls.google_drive_client = GoogleDriveClient.load_from_env(env_prefix='GOOGLE_DRIVE_')

    def test_retrieve_folder_id(self):
        folder_name = 'test-coa-aprp-dailyreport'
        response = self.google_drive_client.search_by_name(folder_name, mimetype=self.google_drive_client.FOLDER_MIME_TYPE)
        self.assertEqual(response[0]['id'], self.test_folder_id)

    def test_file_upload_publish(self):
        response = self.google_drive_client.media_upload(
            name='test',
            file_path=str(settings.BASE_DIR('google_api/google_drive/file1.xlsx')),
            from_mimetype=self.google_drive_client.XLSX_MIME_TYPE,
            parents=[self.test_folder_id],
        )

        file_id = response.get('id')
        self.assertIsNotNone(file_id)

        # make public read permission
        self.google_drive_client.set_public_permission(file_id)

        # update with different file
        self.google_drive_client.media_update(file_id=file_id,
                                              file_path=str(settings.BASE_DIR('google_api/google_drive/file2.csv')),
                                              from_mimetype='text/csv')
