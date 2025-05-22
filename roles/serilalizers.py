from rest_framework import serializers
from roles.models import Permission, PermissionCategory, Role
from web.serializers.block_category_serializer import BlockCategorySerializer
from web.models import BlockCategory
from web.serializers.brand_serializer import BrandOwnerSerializer, OwnerSerializer


class PermissionSerializer(serializers.ModelSerializer):
    category = serializers.CharField()

    class Meta:
        model = Permission
        fields = [
            "id",
            'excludes',
            "component_key",
            "label",
            "description",
            "is_active",
            "category",
            "dependent_permission",
            "excludes",
        ]


class PermissionCategorySerializer(serializers.ModelSerializer):
    child = PermissionSerializer(many=True)

    class Meta:
        model = PermissionCategory
        fields = ("id", "label", "description", "group_type", "child")


class RoleSerializer(serializers.ModelSerializer):
    block_category = BlockCategorySerializer(many=True)
    permissions = PermissionSerializer(many=True)
    brand_owner = OwnerSerializer()
    creator = serializers.CharField()

    class Meta:
        model = Role
        fields = [
            "id",
            "brand_owner",
            "label",
            "is_active",
            "creator",
            "created_at",
            "permissions",
            "block_category",
            "is_superuser",
            "key_code",
            "is_immuteable"
        ]


class MinimalRoleSerializer(serializers.ModelSerializer):
    block_category = BlockCategorySerializer(many=True)
    brand_owner = serializers.CharField()
    creator = serializers.CharField()

    class Meta:
        model = Role
        fields = [
            "id",
            "brand_owner",
            "label",
            "is_active",
            "creator",
            "created_at",
            "block_category",
            "is_superuser",
            "key_code",
        ]


class RoleCreateSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.order_by('order'), many=True
    )
    block_category = serializers.PrimaryKeyRelatedField(
        queryset=BlockCategory.objects.all(), many=True
    )

    class Meta:
        model = Role
        fields = [
            "label",
            # "brand_owner",
            "id",
            "key_code",
            "block_category",
            "permissions",
            "is_active",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data.pop("creator", None)
        validated_data.pop("brand_owner", None)  # Remove brand_owner to avoid duplication
        permissions = validated_data.pop("permissions")
        block_category = validated_data.pop("block_category")

        role = Role.objects.create(creator=user, brand_owner=user.affiliation, **validated_data)
        role.permissions.set(permissions)
        role.block_category.set(block_category)
        return role


class UserPermissionComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "component_key",
        ]


class SimpleUserRoleSerializer(serializers.ModelSerializer):
    label = serializers.CharField()
    is_active = serializers.BooleanField()
    permissions = UserPermissionComponentSerializer(many=True)

    class Meta:
        model = Role
        fields = (
            'permissions',
            'label',
            'is_active',
        )
