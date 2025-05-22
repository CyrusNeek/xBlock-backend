from rest_framework import serializers
from web.models import OTP

class OTPSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    
    class Meta:
        model = OTP
        fields = ['user', 'email', 'phone_number', 'otp_code', 'created_at', 'expires_at']
