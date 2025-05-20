from rest_framework import serializers
from web.constants import WhisperLanguages
from web.models import Task, User
from web.models.category import Category
from web.serializers import TaskSerializer, UserSerializer
from vtk.models import XClassmate
from web.serializers.category_serializer import CategoryFlatSerializer, CategorySerializer


class XClassmateListSerializer(serializers.ModelSerializer):
    # participants = serializers.IntegerField(source='participants.count', read_only=True)
    participants = serializers.IntegerField(source="participants_count", read_only=True)
    task_count = serializers.IntegerField(read_only=True)

    category = CategoryFlatSerializer(read_only=True)  
    sub_category = CategoryFlatSerializer(read_only=True)
    # file = serializers.FileField(required=False)

    class Meta:
        model = XClassmate
        fields = (
            "id",
            "name",
            "key_points",
            "length",
            "participants",
            # 'tasks',
            "diarization_triggered",
            "created_at",
            "created_by",
            "task_count",
            "is_added_xbrain",
            "is_added_report",
            "tags",
            "category",
            "sub_category",
            "purpose",
            "summary",
            "diarization_id",
            "file_id",
            "full_content"
            
        )


class XClassmateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "created_at",
            "full_name",
        )


class XClassmateSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField(read_only=True)
    participants_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, required=False
    )
    participants_count = serializers.SerializerMethodField(read_only=True)
    source_language = serializers.ChoiceField(
        choices=WhisperLanguages.choices(), default=WhisperLanguages.ENGLISH.value
    )
    target_language = serializers.ChoiceField(
        choices=WhisperLanguages.choices(), default=WhisperLanguages.SPANISH.value
    )

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    sub_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = XClassmate
        fields = "__all__"
        extra_kwargs = {"participants_ids": {"required": True}}

    def get_tasks(self, obj):
        tasks = Task.objects.select_related(
            "created_by", "assignee", "xclassmate", "unit"
        ).filter(xclassmate=obj)
        return TaskSerializer(tasks, many=True).data

    def get_participants(self, obj):
        return UserSerializer(obj.participants.all(), many=True).data

    def get_participants_count(self, obj):
        return obj.participants.count()

    def create(self, validated_data):
        user = self.context["request"].user

        # Remove the recording data from validated_data if present
        recording_data = validated_data.pop("recording", None)
        participants_ids = validated_data.pop("participants_ids", [])

        # Create the xclassmate instance without the recording
        xclassmate = XClassmate(**validated_data)
        xclassmate.created_by = user
        xclassmate.save()

        if user.id not in participants_ids:
            participants_ids.append(user.id)
        xclassmate.participants.set(participants_ids)

        # Resave the xclassmate, so we can have id field in the file path
        if recording_data:
            xclassmate.recording = recording_data
            xclassmate.save()

        return xclassmate

    def update(self, instance, validated_data):
        # The corrected key is 'participants' because of the source argument implications
        if "participants_ids" in validated_data:
            participant_ids = validated_data.pop(
                "participants_ids"
            )  # Use the correct key
            instance.participants.set(participant_ids)

        # Handle other fields as necessary
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UpdateDiarizationRequestSerializer(serializers.Serializer):
    speaker = serializers.CharField(default="Speaker_01")
    user_id = serializers.IntegerField(required=False)
    new_speaker = serializers.CharField(required=False)