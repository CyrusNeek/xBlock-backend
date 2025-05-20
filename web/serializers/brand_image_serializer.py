from rest_framework import serializers
from web.models import Brand
from web.services.google_bucket import GoogleBucket
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os

class BrandImageSerializer(serializers.ModelSerializer):
    brand_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Brand
        fields = ['brand_image']

    

    # def update(self, instance, validated_data):
    #     brand_image = validated_data.pop('brand_image', None)

    #     # Delete old brand image if a new one is being uploaded
    #     if brand_image and instance.brand_image_url:
    #         self._delete_old_brand_image(instance)

    #     if brand_image:
    #         local_path = self._save_image_locally(brand_image)

    #         google_bucket = GoogleBucket()
    #         destination = f"brand_images/{instance.username}/{brand_image.name}"
    #         google_bucket.upload_file(local_path, destination)

    #         public_url = google_bucket.generate_presigned_download_url(destination, None)[0]
    #         instance.brand_image_url = public_url

    #         os.remove(local_path)

    #     return super().update(instance, validated_data)
    
    

    # def _save_image_locally(self, image):
    #     path = f'temporary_uploads/{image.name}'
    #     full_path = default_storage.save(path, ContentFile(image.read()))
    #     return default_storage.path(full_path)

    # def _delete_old_brand_image(self, instance):
    #     bucket_name = settings.GOOGLE_STORAGE_BUCKET_NAME
    #     blob_name = instance.brand_image_url.split(f"{bucket_name}/")[-1]

    #     google_bucket = GoogleBucket()
    #     google_bucket.delete_file(blob_name)
