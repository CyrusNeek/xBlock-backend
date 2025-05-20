from rest_framework import serializers
from web.models import Chat
from web.serializers import UserSerializer

class ThreadChatSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Chat
        fields = [
            "id",
            "prompt",
            "chat_type",
            "thread", 
            "user"    ,
            "role"       
        ]