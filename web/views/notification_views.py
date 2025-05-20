from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from web import pagination
from web.models import Notification
from web.serializers import NotificationSerializer
from web.pagination import NotificationPagination

class HasUnreadNotificationsView(APIView):
    """
    View to check if there are any unread notifications for a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        has_unread = Notification.objects.select_related("user").filter(user=user, is_read=False).exists()
        return Response({"has_unread": has_unread})

class NotificationsView(APIView):
    """
    View to list all unread notifications for a user and mark them as read.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        # David: remove  is_read=False from query
        notifications = Notification.objects.select_related('user').filter(user=user)

        # Apply pagination
        paginator = NotificationPagination()
        paginated_notifications = paginator.paginate_queryset(notifications, request)
        
        # Serialize the paginated notifications
        serialized_data = NotificationSerializer(paginated_notifications, many=True).data

        # Mark notifications as read after serialization
        notifications.update(is_read=True)
        
        # Return paginated response
        return paginator.get_paginated_response(serialized_data)
