from rest_framework import serializers
from ..models import User, UserBrand
from roles.models import Role, Permission
from web.serializers.unit_serializer import UnitSerializer
from roles.serilalizers import (
    UserPermissionComponentSerializer,
    RoleSerializer,
    SimpleUserRoleSerializer,
)
from django.db import transaction
import random
from web.services.storage_service import StorageService
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), write_only=True, required=False
    )
    tokens = serializers.IntegerField(read_only=True)
    minutes = serializers.IntegerField(read_only=True)
    role_name = serializers.CharField(source="role", read_only=True)
    multi_factor_auth = serializers.BooleanField(read_only=True)

    unit = UnitSerializer(read_only=True)
    role_data = SimpleUserRoleSerializer(read_only=True, source="role")
    email = serializers.EmailField()

    profile_image_url = serializers.SerializerMethodField()

    def get_profile_image_url(self, obj):
        if not obj.profile_image_url:
            return ""
        url_validator = URLValidator()
        try:
            url_validator(obj.profile_image_url)
            return obj.profile_image_url
        except ValidationError:
            return StorageService().generate_presigned_download_url(obj.profile_image_url)

        

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_email_verified",
            "password",
            "unit",
            "first_name",
            "last_name",
            "team",
            "manager",
            "role_name",
            "name",
            "display_name",
            "phone_number",
            "is_phone_verified",
            "secondary_email",
            "is_secondary_email_verified",
            "timezone",
            "profile_image_url",
            "paytype",
            "rate",
            "role",
            "role_id",
            "units",
            "is_active",
            "affiliation",
            "role_data",
            "multi_factor_auth",
            "personal_info",
            "tokens",
            "minutes",
            "account_type",
            "wizard_status",
            "is_super_user",
            "position"
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "team": {"required": True},
            "manager": {"required": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        role = instance.role

        if role:
            if role.is_superuser:
                permissions = Permission.objects.filter(is_active=True).all()
            else:
                permissions = instance.role.permissions
        else:
            permissions = None

        representation["role_data"] = {
            "permissions": UserPermissionComponentSerializer(
                permissions, many=True
            ).data
        }

        return representation

    def create(self, validated_data):
        with transaction.atomic():
            units = validated_data.pop("units", [])
            password = validated_data.pop("password", None)
            user = super().create(validated_data)

            if password:
                user.set_password(password)
                user.save()

            self._update_user_units_and_brands(user, units)
            return user

    def update(self, instance, validated_data):
        with transaction.atomic():
            print(f"Incoming validated data: {validated_data}")  # Debugging statement

            units = validated_data.pop("units", None)
            password = validated_data.pop("password", None)
            user = super().update(instance, validated_data)

            if password:
                user.set_password(password)
                user.save()

            if units is not None:
                self._update_user_units_and_brands(user, units)
            return user

    def _update_user_units_and_brands(self, user, units):
        # Debug statement to check if 'request' is in context
        if "request" not in self.context:
            raise KeyError("Request object not found in context")

        # Update the user's units directly
        user.units.set(units)
        user.affiliation = self.context["request"].user.affiliation

        # Get all unique brand IDs from the updated units
        unique_brand_ids = set(unit.brand_id for unit in units)

        # Create or update UserBrand associations for these brands
        for brand_id in unique_brand_ids:
            UserBrand.objects.update_or_create(user=user, brand_id=brand_id)

        # Cleanup: Remove UserBrand associations not related to any of the user's current units' brands.
        user.user_brands.exclude(brand_id__in=unique_brand_ids).delete()
        user.save()


class UserManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserProfileSerializer(serializers.ModelSerializer):
    role_data = RoleSerializer(source="role", read_only=True)
    is_email_verified = serializers.BooleanField(read_only=True)
    multi_factor_auth = serializers.BooleanField(read_only=True)

    # List of allowed keys for personal_info
    ALLOWED_PERSONAL_INFO_KEYS = {
        "x",
        "linkedin",
        "personal_blog",
        "personal_website",
        "description",
    }

    def __init__(self, *args, **kwargs):
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

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
        internal_value["personal_info"] = personal_info_data
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

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_email_verified",
            "display_name",
            "phone_number",
            "role_data",
            "unit",
            "multi_factor_auth",
            "profile_image_url",
            "tokens",
            "minutes",
        ]
        read_only_fields = [
            "profile_image_url",
            "tokens",
            "minutes",
            "is_email_verified",
            "role_data",
            "unit",
            "multi_factor_auth",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'otp_secret','account_type']  

    def validate(self, attrs):
        """Convert username and email to lowercase before saving."""
        attrs['username'] = attrs['username'].lower()
        attrs['email'] = attrs['email'].lower()
        return attrs
        

    def create(self, validated_data):
        otp_secret = validated_data.get('otp_secret', generate_otp_secret())  
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            account_type=validated_data['account_type'],
        )
        
        user.is_active=False
        user.otp_secret = otp_secret
        user.save()
        return user
    

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_image_url','account_type','position','unit'] 
        extra_kwargs = {"file": {"required": True}}

class UserWizardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['wizard_status'] 
    

def generate_otp_secret(length=6):
    """Generate a random OTP secret of the specified length (default is 6 digits)."""
    otp_secret = ''.join(random.choices('0123456789', k=length))
    return otp_secret


