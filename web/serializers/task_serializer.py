from rest_framework import serializers
from ..models import Task
from web.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "unit",
            "first_name",
            "last_name",
            "name",
            "phone_number",
            "secondary_email",
            "timezone",
            "profile_image_url",
        ]


class TaskSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField(read_only=True)
    assignee = UserSerializer(read_only=True)
    # Remove or comment out the created_by field here.
    meeting_name = serializers.CharField(source="meeting.name", read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        write_only=True, 
        queryset=User.objects.all(), 
        source='assignee', 
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "creator_name",
            # "created_by",  # This is removed from the fields list.
            "assignee",
            "status",
            "created_at",
            "description",
            "meeting",
            "due_date",
            "meeting_name",
            "assignee_id",
            "assigned_date",
        ]
        
    def get_creator_name(self, obj):
        # Assuming the User model has a 'name' field. Adjust as per your User model's structure.
        return (
            obj.created_by.first_name + " " + obj.created_by.last_name
            if obj.created_by
            else None
        )
