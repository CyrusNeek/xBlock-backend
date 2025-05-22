from rest_framework import serializers
from web.models import User
from web.models import LLMChat
from web.serializers import UserSerializer

class LLMChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = LLMChat
        fields = ('id', 'user', 'messages','title','created_at')