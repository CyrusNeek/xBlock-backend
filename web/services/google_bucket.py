import json
import os
from google.cloud import storage
from django.conf import settings

import datetime


class GoogleBucket:
    storage_client = storage.Client.from_service_account_json("credentials.json")

    bucket = storage_client.bucket(settings.GOOGLE_STORAGE_BUCKET_NAME)

    # instance = None

    def download_file(self, source, destination):
        blob = self.bucket.blob(source)
        blob.download_to_filename(destination)

        return blob

    def upload_file(self, source, destination):
        blob = self.bucket.blob(destination)

        generation_match_precondition = 0

        blob.upload_from_filename(
            source, if_generation_match=generation_match_precondition
        )

        return blob

    def generate_presigned_download_url(self, destination, expire_at):
        blob = self.bucket.blob(destination)

        if expire_at is None:
            expire_at = datetime.timedelta(minutes=15)

        url = blob.generate_signed_url(
            version="v4",
            expiration=expire_at,
            method="GET",
        )

        return url, {}

    def generate_presigned_upload_url(self, destination, expire_at=None):

        if expire_at is None:
            expire_at = datetime.timedelta(minutes=15)

        policy = self.storage_client.generate_signed_post_policy_v4(
            settings.GOOGLE_STORAGE_BUCKET_NAME,
            destination,
            expiration=datetime.timedelta(seconds=expire_at),
        )

        return policy["url"], policy["fields"]

    def download_files_from_directory(self, prefix, local_dir):
        blobs = self.bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            if not blob.name.endswith("/"):  # Skip directories
                local_file_path = os.path.join(
                    local_dir, os.path.relpath(blob.name, prefix)
                )
                local_file_dir = os.path.dirname(local_file_path)
                if not os.path.exists(local_file_dir):
                    os.makedirs(local_file_dir)
                print(f"Downloading {blob.name} to {local_file_path}...")
                blob.download_to_filename(local_file_path)
        print("Download complete.")

    def delete_file(self, destination):
        blob = self.bucket.blob(destination)
        blob.delete()
        return True

    def upload_or_replace(self, source, destination):
        blob = self.bucket.blob(destination)

        if blob.exists():
            blob.delete()

        self.upload_file(source, destination)
        return blob