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
from django.db.models import Q


# Serializer for Thread Model
class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = [
            "id",
            "created_at",
            "title"
        ]

class ThreadPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'  # Allow the client to set page size
    max_page_size = 50 


# ViewSet for Thread Chat
class ThreadChatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer
    pagination_class = ThreadPagination  # Add pagination here

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        thread_id = data.get("threadId")
        if not thread_id:
            # Create a new thread if threadId is not provided
            thread = self.create_thread(data, user)
            data["threadId"] = thread.id
        else:
            # Validate and retrieve existing thread
            thread = Thread.objects.filter(id=thread_id).first()
            if not thread:
                raise ValidationError({"thread": "Invalid thread ID provided."})

        # Serialize the chat data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        chat = serializer.save(user=user, thread=thread)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Thread.objects.filter(
            user=self.request.user
            
        ).filter( Q(is_assistant_thread=False) | Q(is_assistant_thread__isnull=True)).order_by("created_at")

    @staticmethod
    def create_thread(data, user):
        """Helper method to create a new thread."""
        prompt = data.get("prompt", "New Thread")
        thread_title = prompt[:50]  # Use first 50 characters of prompt as title
        return Thread.objects.create(user=user, title=thread_title)