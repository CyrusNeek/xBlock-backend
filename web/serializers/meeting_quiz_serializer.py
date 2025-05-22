from rest_framework import serializers
from web.models.meeting_quiz import MeetingQuiz


class MeetingQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingQuiz
        fields = "__all__"