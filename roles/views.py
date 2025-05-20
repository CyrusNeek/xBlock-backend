from django.db.models import Prefetch
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import Permission, PermissionCategory, Role
from .serilalizers import PermissionCategorySerializer, RoleCreateSerializer, RoleSerializer
from rest_framework.validators import ValidationError
from .permissions import UserPermission
from .constants import UNLIMITED_CRUD_ROLE_ACCESS
from rest_framework.response import Response
from rest_framework import status

           
class PermissionCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PermissionCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PermissionCategory.objects.filter(is_active=True).prefetch_related(
            Prefetch('child', queryset=Permission.objects.filter(is_active=True).order_by('order'))
        ).order_by('order')
        
class RoleViewSet(viewsets.ModelViewSet):    
    required_permission = UNLIMITED_CRUD_ROLE_ACCESS
    permission_classes = [UserPermission]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RoleCreateSerializer
        return RoleSerializer
    
    def get_queryset(self):
        return Role.objects.select_related("creator", "brand_owner")\
            .prefetch_related("permissions", "block_category")\
            .filter(brand_owner=self.request.user.affiliation)\
            .distinct()

    def perform_create(self, serializer):
        permissions_data = serializer.validated_data.get('permissions', [])
        
        # Track permissions to be added
        permissions_to_add = set(permissions_data)
        permissions_to_exclude = set()

        # Add any permissions that are dependent on the selected permissions
        for permission in permissions_data:
            # Check if the permission is active
            if not permission.is_active:
                raise ValidationError(f"Permission '{permission}' is not active.")
            
            # Find all permissions that depend on this permission
            dependent_permissions = Permission.objects.filter(dependent_permission=permission)
            for dep_perm in dependent_permissions:
                permissions_to_add.add(dep_perm)
                
            # Collect excluded permissions
            permissions_to_exclude.update(permission.excludes.all())
        
        # Check for conflicts with excluded permissions
        conflicting_permissions = permissions_to_add.intersection(permissions_to_exclude)
        if conflicting_permissions:
            conflicting_labels = ', '.join(p.label for p in conflicting_permissions)
            raise ValidationError(f"The selected permissions include exclusions: {conflicting_labels}")

        # Set the final permissions and block categories
        role = serializer.save(creator=self.request.user, brand_owner=self.request.user.affiliation)
        role.permissions.set(permissions_to_add)
        role.block_category.set(serializer.validated_data.get('block_category', []))

    def perform_destroy(self, instance):
        if instance.is_immuteable:  
            raise ValidationError("You cannot delete Super Admin Role.")
        
        instance.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
