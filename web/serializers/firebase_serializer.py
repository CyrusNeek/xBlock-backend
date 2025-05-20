from rest_framework import serializers

class FirebaseCloudMessagingSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)

    def validate_token(self, value):
        # You can add any custom validation for the token here if needed.
        if not value:
            raise serializers.ValidationError("Token is required.")
        return value
