import os

from .s3 import S3Client
from .google_bucket import GoogleBucket


class StorageService:
    def __init__(self):
        if os.getenv("AMAZON_DEPLOYMENT", "false") == "true":
            self.client = S3Client()
        else:
            self.client = GoogleBucket()

    def download_file(self, source, destination):
        return self.client.download_file(source, destination)

    def upload_file(self, source, destination):
        return self.client.upload_file(source, destination)

    def generate_presigned_download_url(self, destination, expire_at=3600):
        return self.client.generate_presigned_download_url(destination, expire_at)

    def generate_presigned_upload_url(self, destination, expire_at=3600):
        return self.client.generate_presigned_upload_url(destination, expire_at)
