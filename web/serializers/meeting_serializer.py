from rest_framework import serializers
from web.constants import WhisperLanguages
from web.models.category import Category
from web.serializers.category_serializer import CategoryFlatSerializer
from ..models import Meeting, Task
from .task_serializer import TaskSerializer
from web.models import User
from web.serializers import UserSerializer
import pytz

class MeetingListSerializer(serializers.ModelSerializer):
    # participants = serializers.IntegerField(source='participants.count', read_only=True)
    participants = serializers.IntegerField(source='participants_count', read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    category = CategoryFlatSerializer(read_only=True)  
    sub_category = CategoryFlatSerializer(read_only=True)
    class Meta:
        model = Meeting
        fields = (
            'id',
            'name',
            'key_points',
            'length',
            'participants',
            # 'tasks',
            'diarization_triggered',
            'diarization_id',
            'diarization_signal_triggered',
            'created_at',
            'task_count',
            'category',
            'sub_category',
            'purpose',
            'tags',
            'is_added_xbrain',
            'is_added_report',
            'summary',
            'file_id',
            'start_date',
            'end_date',
            'timezone',
            'repeat_period',
            'held_type',


        )

    # def get_tasks(self, obj):
    #     return Task.objects.select_related("created_by", "assignee", "meeting", "unit").filter(meeting=obj).count()


class MeetingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'created_at', 'full_name', )

class MeetingSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField(read_only=True)
    participants_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    participants_count = serializers.SerializerMethodField(read_only=True)
    # source_language = serializers.ChoiceField(choices=WhisperLanguages.choices(), default=WhisperLanguages.ENGLISH.value)
    # target_language = serializers.ChoiceField(choices=WhisperLanguages.choices(), default=WhisperLanguages.SPANISH.value)
    
    # category = CategoryFlatSerializer(read_only=True)  
    # sub_category = CategoryFlatSerializer(read_only=True)

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    sub_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    

    class Meta:
        model = Meeting
        fields = "__all__"
        extra_kwargs = {
            'participants_ids': {'required': True} ,
            'file_ids' : {"required": False}
        }

    def validate(self, data):
        MEETING_HELD_TYPE = [
            ("In-Person", "In-Person"),
            ("Online", "Online"),
            ("Hybrid", "Hybrid")
        ]
        
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        held_type = data.get("held_date")
        timezone = data.get("timezone")
        repeat_period = data.get("repeat_period")




        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before start date."})
        
        if held_type and held_type not in self.MEETING_HELD_TYPE:
            raise serializers.ValidationError({"held_type": f"Held type must be one of {', '.join(self.MEETING_HELD_TYPE)}."})

        if timezone and timezone not in pytz.all_timezones:
            raise serializers.ValidationError({"timezone": "Invalid timezone. Use a valid IANA timezone (e.g., 'UTC', 'America/New_York')."})

        if repeat_period is not None:
            try:
                repeat_period = int(repeat_period)
                if repeat_period <= 0:
                    raise ValueError
            except ValueError:
                raise serializers.ValidationError({"repeat_period": "Repeat period must be a positive integer."})


        return data


    def get_tasks(self, obj):
        tasks = Task.objects.select_related("created_by", "assignee", "meeting", "unit").filter(meeting=obj)
        return TaskSerializer(tasks, many=True).data
    
    def get_participants(self, obj):
        return UserSerializer(obj.participants.all(), many=True).data
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    
    def create(self, validated_data):
        user = self.context["request"].user

        # Remove the recording data from validated_data if present
        recording_data = validated_data.pop("recording", None)
        participants_ids = validated_data.pop('participants_ids', [])

        # Create the Meeting instance without the recording
        meeting = Meeting(**validated_data)
        meeting.created_by = user
        meeting.save()

        if user.id not in participants_ids:
            participants_ids.append(user.id)
        meeting.participants.set(participants_ids)
        
        # Resave the meeting, so we can have id field in the file path
        if recording_data:
            meeting.recording = recording_data
            meeting.save()


        return meeting
    

    def update(self, instance, validated_data):
        # The corrected key is 'participants' because of the source argument implications
        if 'participants_ids' in validated_data:
            participant_ids = validated_data.pop('participants_ids')  # Use the correct key
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
