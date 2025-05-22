from rest_framework.permissions import BasePermission
from roles.models import Permission
from django.db.models import Q


class UserPermission(BasePermission):
    """
    Custom permission class to check user permissions based on roles and specific permissions.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        required_permission = getattr(view, 'required_permission', None)
        if required_permission is None:
            return False

        return self.user_has_permission(user, required_permission)

    @staticmethod
    def user_has_permission(user, required_permission):
        """
        Check if the user has the required permission.

        Args:
            user (User): The user object.
            required_permission (str): The permission label to check.

        Returns:
            bool: True if the user has the required permission, False otherwise.
        """
        try:
            if user.role.is_superuser:
                return True
            return Permission.objects.filter(Q(component_key__in=required_permission) | Q(component_key=required_permission), role=user.role, is_active=True).exists()

        except:
            return False

    @staticmethod
    def check_user_permission(user, required_permissions):
        """
        Check if the user has any of the required permissions.

        Args:
            user (User): The user object.
            required_permissions (list): A list of permission labels to check.

        Returns:
            bool: True if the user has any of the required permissions, False otherwise.
        """
        try:
            if user.role.is_superuser:
                return True

            if isinstance(required_permissions, str):
                required_permissions = [required_permissions]

            return Permission.objects.filter(role=user.role, component_key__in=required_permissions, is_active=True).exists()
        except:
            return False
