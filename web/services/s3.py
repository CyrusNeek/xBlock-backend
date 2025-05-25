from django.conf import settings

# AWS S3 client deprecated and removed
    UNIT_FILE_FOLDER = "unit-file"
    MEETING_FOLDER = "meetings"
    SSH_KEYS_FOLDER = "sshkeys"

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    def upload_file(self, source, destination):
        return self.s3_client.upload_file(
            source, settings.AWS_STORAGE_BUCKET_NAME, destination
        )

    def download_file(self, source, destination):
        file = self.s3_client.download_file(
            settings.AWS_STORAGE_BUCKET_NAME, source, destination
        )

        return open(destination)

    def download_url(self, storage_name, filename):
        filename = filename.split("/")[-1]
        presigned_url = S3Client.generate_presigned_url(
            folder=storage_name,
            file_name=filename,
        )

        response = requests.get(presigned_url)
        with open(filename, "wb") as file:
            file.write(response.content)

        return filename

    def generate_presigned_download_url(self, pathname, expire_at=3600):
        """Generate a presigned URL to access a file. The file_path should include the path within the bucket."""
        presigned_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": pathname,
            },
            ExpiresIn=expire_at,
        )

        return presigned_url

    def generate_presigned_upload_url(self, pathname, expire_at=3600):
        presigned_post = self.s3_client.generate_presigned_post(
            ExpiresIn=expire_at,
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=pathname,
        )

        return presigned_post["url"] + pathname, presigned_post["fields"]

    @classmethod
    def generate_presigned_url(cls, folder, file_name):
        """Generate a presigned URL to access a file. The file_path should include the path within the bucket."""
        presigned_url = cls.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": f"{folder}/{file_name}",
            },
            ExpiresIn=3600,
        )
        return presigned_url

    @classmethod
    def generate_presigned_post_url(cls, folder, file_name):
        """Generate a presigned POST URL for uploading a file."""
        presigned_post = cls.s3_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=f"{folder}/{file_name}",
            ExpiresIn=3600,
        )
        return presigned_post


# Example usage
# if __name__ == "__main__":

#     s3 = S3Client(settings)
#     presigned_url = s3.generate_presigned_url("path/to/meeting/recording.mp4")
#     print("Presigned GET URL:", presigned_url)

#     presigned_post_url = s3.generate_presigned_post_url("new_upload.mp4")
#     print("Presigned POST URL:", presigned_post_url)
