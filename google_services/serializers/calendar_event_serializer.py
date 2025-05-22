from rest_framework import serializers

class EventSerializer(serializers.Serializer):
    id = serializers.CharField()
    created = serializers.DateTimeField(required=False, allow_null=True)
    updated = serializers.DateTimeField(required=False, allow_null=True)
    summary = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    creator = serializers.EmailField(required=False, allow_blank=True)
    start = serializers.JSONField()
    end = serializers.JSONField()
    attendees = serializers.ListField(child=serializers.JSONField(), required=False)
    conferenceData = serializers.JSONField(required=False, allow_null=True)
    
    
class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=False, input_formats=['%Y-%m-%d'])
    end_date = serializers.DateTimeField(required=False, input_formats=['%Y-%m-%d'])