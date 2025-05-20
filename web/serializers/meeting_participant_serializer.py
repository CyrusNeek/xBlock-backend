from rest_framework import serializers
from web.models import MeetingParticipant

class MeetingParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingParticipant
        fields = '__all__' 
