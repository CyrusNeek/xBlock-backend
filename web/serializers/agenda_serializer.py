from rest_framework import serializers
from web.models import Meeting, Agenda

class AgendaSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() 

    class Meta:
        model = Agenda
        fields = ['id', 'meeting', 'title', 'description', 'time_allotted', 'user', 'speaker_name']

    def validate_time_allotted(self, value):
        if value <= 0:
            raise serializers.ValidationError("Time allotted must be a positive integer.")
        return value

