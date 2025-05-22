from rest_framework import serializers
from web.models import Brand, BrandOwner
from web.services.google_bucket import GoogleBucket
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from web.models import Unit, UserBrand
from web.serializers.unit_serializer import UnitSerializer
import os
from web.services.storage_service import StorageService

class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandOwner
        fields = [
            "id",
            "name",
            "description",
            "public_business_name",
            "email",
            "zip_code",
            
        ]
        
class BrandSerializer(serializers.ModelSerializer):
    
    brand_image_url = serializers.SerializerMethodField()
    units = serializers.SerializerMethodField()
    owner = OwnerSerializer(read_only=True)

    def get_units(self, obj):
        from web.serializers import UnitSerializer
        user = self.context["request"].user
        # units_queryset = obj.units.all().intersection(user.all_units.all())
        units_queryset = Unit.objects.filter(brand=obj).all()
        serializer = UnitSerializer(units_queryset, many=True)
        return serializer.data
    
    def get_brand_image_url(self, obj):
        if obj.brand_image_url:
            return StorageService().generate_presigned_download_url(obj.brand_image_url)
        else:
            return ""
    
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "owner",
            "brand_image_url",
            "affiliation",
            "website",
            "units",
            "address",
            "email",
            "description"
        ]

class BrandCreateSerializer(serializers.ModelSerializer):
    brand_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Brand
        fields = ["id","name", "email", "website", "address", "brand_image", "description","owner"]

    def create(self, validated_data):
        user = self.context['request'].user
        
        # Fetch the user's brand from UserBrand model
        try:
            user_brand = UserBrand.objects.filter(user=user).first()
        except UserBrand.DoesNotExist:
            raise serializers.ValidationError("User does not have an associated brand.")

        brand = Brand.objects.get(pk=user_brand.brand.id)
        # Set the owner to the user's brand
        validated_data['owner'] = brand.owner

        # Set affiliation to None if it was provided
        validated_data['affiliation'] = None

        # Handle brand image if provided
        brand_image = validated_data.pop('brand_image', None)
        instance = super().create(validated_data)

        if brand_image:
            local_path = self._save_image_locally(brand_image)

            google_bucket = GoogleBucket()
            destination = f"brand_images/{instance.id}/{brand_image.name}"
            google_bucket.upload_file(local_path, destination)
            public_url = google_bucket.generate_presigned_download_url(destination, None)[0]

            instance.brand_image_url = public_url
            instance.save()

            os.remove(local_path)
        
        return instance

    def _save_image_locally(self, image):
        path = f'temporary_uploads/brands/{image.name}'
        full_path = default_storage.save(path, ContentFile(image.read()))
        return default_storage.path(full_path)

class BrandOwnerSerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True, read_only=True)

    class Meta:
        model = BrandOwner
        fields = [
            "id",
            "name",
            "description",
            "public_business_name",
            "timezone",
            "email",
            "is_email_verified",
            "phone_number",
            "is_phone_verified",
            "account_name",
            "zip_code",
            "address",
            "state",
            "city",
            "brands",
            "address2",
            "workspace_type",
        ]

class BrandInitSerializer(serializers.ModelSerializer):
    workspace_type = serializers.CharField(required=True)
    primary_brand_name = serializers.CharField(required=True)
    sub_brand_name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    website = serializers.URLField(required=True)
    location = serializers.CharField(required=True)

    class Meta:
        model = Brand
        fields = [
            "id",
            "workspace_type",
            "primary_brand_name",
            "sub_brand_name",
            "address",
            "website",
            "location",
            "unit_name",
        ]

    
