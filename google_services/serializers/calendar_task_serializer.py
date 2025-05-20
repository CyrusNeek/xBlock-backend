from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    created = serializers.DateTimeField(required=False, allow_null=True)
    updated = serializers.DateTimeField(required=False, allow_null=True)
    title = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)