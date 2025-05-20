from rest_framework import serializers
from web.models import MeetingAddress

class MeetingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAddress
        fields = '__all__' 
