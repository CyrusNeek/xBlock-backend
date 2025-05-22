from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import serializers
from web.models import User
from web.services.google_bucket import GoogleBucket
from django.conf import settings
import os

class UserProfileImageSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(write_only=True)

    class Meta:
        model = User
        fields = ('profile_image', 'profile_image_url')

    def update(self, instance, validated_data):
        profile_image = validated_data.pop('profile_image', None)

        # Delete old profile image if a new one is being uploaded
        if profile_image and instance.profile_image_url:
            self._delete_old_profile_image(instance)

        if profile_image:
            local_path = self._save_image_locally(profile_image)
            google_bucket = GoogleBucket()
            destination = f"profile_images/{instance.username}/{profile_image.name}"
            google_bucket.upload_file(local_path, destination)

            public_url = google_bucket.generate_presigned_download_url(destination, None)[0]
            instance.profile_image_url = public_url
            os.remove(local_path)

        return super().update(instance, validated_data)

    def _save_image_locally(self, image):
        path = f'temporary_uploads/user_profile/{image.name}'
        full_path = default_storage.save(path, ContentFile(image.read()))
        return default_storage.path(full_path)

    def _delete_old_profile_image(self, instance):
        bucket_name = settings.GOOGLE_STORAGE_BUCKET_NAME
        blob_name = instance.profile_image_url.split(f"{bucket_name}/")[-1]
        google_bucket = GoogleBucket()
        google_bucket.delete_file(blob_name)
