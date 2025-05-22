from rest_framework import serializers
from web.models import Unit, Brand  


class UnitBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
        ]

class BrandUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = [
            "id",
            "name",
        ]

class UnitSerializer(serializers.ModelSerializer):
    # brand = UnitBrandSerializer()
    class Meta:
        model = Unit
        fields = [
            "id",
            "name",
            "description",
            "address",
            "city",
            "state",
            "zip_code",
            "phone_number",
            "is_phone_verified",
            "email",
            "is_email_verified",
            "website",
            "brand"
        ]

class UnitGetSerializer(serializers.ModelSerializer):
    brand = UnitBrandSerializer()
    class Meta:
        model = Unit
        fields = [
            "id",
            "name",
            "description",
            "address",
            "city",
            "state",
            "zip_code",
            "phone_number",
            "is_phone_verified",
            "email",
            "is_email_verified",
            "website",
            "brand"
        ]
