import os
from django.conf import settings

class StorageService:
    UNIT_FILE_FOLDER = "unit-file"
    MEETING_FOLDER = "meetings"
    SSH_KEYS_FOLDER = "sshkeys"

    def __init__(self):
        self.storage_path = os.path.join(settings.BASE_DIR, 'storage')
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_file_path(self, folder, filename):
        folder_path = os.path.join(self.storage_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        return os.path.join(folder_path, filename)

    def upload_file(self, source, destination):
        target_path = self._get_file_path('uploads', os.path.basename(destination))
        with open(source, 'rb') as src, open(target_path, 'wb') as dst:
            dst.write(src.read())
        return target_path

    def download_file(self, source, destination):
        source_path = self._get_file_path('uploads', os.path.basename(source))
        if os.path.exists(source_path):
            with open(source_path, 'rb') as src, open(destination, 'wb') as dst:
                dst.write(src.read())
            return open(destination, 'rb')
        return None

    def download_url(self, storage_name, filename):
        file_path = self._get_file_path(storage_name, filename)
        if os.path.exists(file_path):
            return file_path
        return None

    def generate_presigned_download_url(self, pathname, expire_at=3600):
        return self._get_file_path('uploads', os.path.basename(pathname))

    def generate_presigned_upload_url(self, pathname, expire_at=3600):
        return self._get_file_path('uploads', os.path.basename(pathname)), {}
