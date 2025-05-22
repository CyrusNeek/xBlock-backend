from rest_framework import serializers
from web.models import User
from vtk.services.bucket_service import get_presigned_post_url
from web.services.storage_service import StorageService
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class UserProfileSerializerNew(serializers.ModelSerializer):
    is_email_verified = serializers.BooleanField(read_only=True)
    # multi_factor_auth = serializers.BooleanField(read_only=True)
    full_name = serializers.CharField(source="first_name")
    profile_image_url = serializers.SerializerMethodField()

    # List of allowed keys for personal_info
    ALLOWED_PERSONAL_INFO_KEYS = {"x", "linkedin", "personal_blog", "personal_website", "description", "job_title"}

    def __init__(self, *args, **kwargs):
        super(UserProfileSerializerNew, self).__init__(*args, **kwargs)

        # Dynamically add fields from personal_info to the serializer
        if self.instance:
            personal_info = (
                self.instance.personal_info
                if isinstance(self.instance.personal_info, dict)
                else {}
            )
            for key, value in personal_info.items():
                if key in self.ALLOWED_PERSONAL_INFO_KEYS:
                    self.fields[key] = serializers.CharField(
                        source=f"personal_info.{key}", required=False
                    )

    def to_representation(self, instance):
        """Convert `instance` to a dict representation."""
        representation = super().to_representation(instance)
        personal_info = instance.personal_info or {}

        # Add personal_info keys to the representation
        for key in self.ALLOWED_PERSONAL_INFO_KEYS:
            if key in personal_info:
                representation[key] = personal_info[key]
            else:
                representation[key] = None

        return representation

    def to_internal_value(self, data):
        """Map incoming data to internal representation."""
        personal_info_data = {}
        for key in self.ALLOWED_PERSONAL_INFO_KEYS:
            if key in data:
                personal_info_data[key] = data.pop(key)

        internal_value = super().to_internal_value(data)
        internal_value['personal_info'] = personal_info_data
        return internal_value

    def update(self, instance, validated_data):
        # Extract personal_info data from validated_data
        personal_info_data = validated_data.pop("personal_info", {})

        # Ensure instance.personal_info is a dictionary
        if instance.personal_info is None:
            instance.personal_info = {}

        # Update only allowed keys in personal_info
        for key, value in personal_info_data.items():
            if key in self.ALLOWED_PERSONAL_INFO_KEYS:
                instance.personal_info[key] = value

        # Update other fields in the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the instance with updated data
        instance.save()
        return instance
    
    def is_valid_url(self, url):
        validator = URLValidator()
        try:
            validator(url)
            return True
        except ValidationError:
            return False


    def get_profile_image_url(self, obj):
        storage_service = StorageService()
        request = self.context.get('request')
        if obj.profile_image_url:  
            if self.is_valid_url(obj.profile_image_url):
                return obj.profile_image_url
            else:
                return storage_service.generate_presigned_download_url(obj.profile_image_url)
        return None 

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "is_email_verified",
            "first_name",
            "last_name",
            # "display_name",
            "phone_number",
            # "unit",
            # "multi_factor_auth",
            "profile_image_url",
            # "tokens",
            # "minutes",
        ]
        read_only_fields = [
            "profile_image_url",
            # "tokens",
            # "minutes",
            "is_email_verified",
            "role",
            # "unit",
            # "multi_factor_auth",
        ]

        