from rest_framework import serializers
from ..models import Group


class GroupSerializer(serializers.ModelSerializer):
    unit_name = serializers.ReadOnlyField(source="unit.name")
    count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = "__all__"
        extra_kwargs = {"unit": {"required": False}, "users": {"required": False}}

    def get_count(self, obj):
        # Return the count of users in the group
        return obj.users.count()
