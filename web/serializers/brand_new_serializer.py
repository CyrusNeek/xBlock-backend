from rest_framework import serializers
from web.models import Brand, BrandOwner
from web.services.google_bucket import GoogleBucket
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from web.models import Unit, UserBrand
from web.serializers.unit_serializer import UnitSerializer
import os

        
class BrandSerializerNew(serializers.ModelSerializer):
    profile_image = serializers.CharField(source="brand_owner_image_url", read_only=True)

    class Meta:
        model = BrandOwner
        fields = [
            "id",
            "profile_image",
            "name",
            "website",
            "address",
            "email",
            "description"
        ]

class BrandOwnerSerializerNew(serializers.ModelSerializer):
    brands = BrandSerializerNew(many=True, read_only=True)

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
        ]
