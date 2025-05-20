from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from web.models import Thread
from web.serializers import ThreadChatSerializer
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from web.models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = [
            "id",
            "prompt",
            "response",
            "created_at",
            "media_url",
        ]

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    
class SingleThreadChatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        """Return chats for a specific thread with pagination."""
        thread_id = self.kwargs.get("thread_id")
        print(thread_id)
        thread = Thread.objects.filter(id=thread_id, user=self.request.user).first()
        if not thread:
            raise ValidationError({"error": "Thread not found or access denied."})

        chats = Chat.objects.filter(thread=thread).order_by("created_at")

        # Apply pagination
        paginator = self.pagination_class()
        paginated_chats = paginator.paginate_queryset(chats, request, view=self)

        # Serialize the paginated data
        serializer = self.get_serializer(paginated_chats, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new chat under a specific thread."""
        thread_id = self.kwargs.get("thread_id")
        thread = Thread.objects.filter(id=thread_id, user=request.user).first()
        if not thread:
            raise ValidationError({"error": "Thread not found or access denied."})
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, thread=thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)