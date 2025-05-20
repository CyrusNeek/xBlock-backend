from rest_framework import viewsets

from roles.constants import LIMITED_TASK_MEETING_CRUD_ACCESS
from ..models import Task
from ..serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from web.pagination import TaskPagination
from roles.permissions import UserPermission

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
        )

    def get_queryset(self):
        return Task.objects.accessible_by_user(self.request.user)

    # def get_object(self):
    #     """Override to add permission checks when accessing a specific task."""
    #     obj = super().get_object()

    #     if not self.request.user.has_task_access(obj):
    #         raise PermissionDenied("You do not have permission to view this task.")
    #     return obj
    
    def check_permission(self, requset):
        return UserPermission.check_user_permission(self.request.user, LIMITED_TASK_MEETING_CRUD_ACCESS)
    
    def perform_permissions_check(self, request):
        if not self.check_permission(request):
            raise PermissionDenied("You don't have permission to perform this action.")
    
    def create(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        return super().destroy(request, *args, **kwargs)
    
    
# --------------------------------------------------
