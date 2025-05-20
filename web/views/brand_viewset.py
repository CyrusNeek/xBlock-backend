from httpx import request
from rest_framework import viewsets
from roles.constants import UNLIMITED_CRUD_BRAND_ACCESS
from web.models import BrandOwner, Brand
from web.serializers import BrandSerializer, BrandCreateSerializer
from web.serializers import BrandOwnerSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from web.models import UserBrand, Unit
from roles.permissions import UserPermission

class UserBrandsViewSet(viewsets.ModelViewSet):
    """
    return Primary brand of user. (Brand's without any affiliation)
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method.lower() == "post":
            return BrandCreateSerializer
        return BrandSerializer
    
    def get_queryset(self):
        user = self.request.user
        brands = Brand.objects.filter(owner__id=user.affiliation.id).prefetch_related("units")
        return brands
        
    def check_permission(self):
        return UserPermission.check_user_permission(self.request.user, UNLIMITED_CRUD_BRAND_ACCESS)
    
    def perform_permissions_check(self):
        if not self.check_permission():
            raise PermissionDenied("You don't have permission to perform this action.")
    
    def create(self, request, *args, **kwargs):
        self.perform_permissions_check()
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.perform_permissions_check()
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.perform_permissions_check()
        return super().destroy(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        brand = serializer.save()
        UserBrand.objects.create(user=self.request.user, brand=brand)

class BrandOwnerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = BrandOwner.objects.all()
    serializer_class = BrandOwnerSerializer

    def get_queryset(self):
        """
        Return the brand owner associated with the authenticated user's affiliation.
        """
        # Ensure the user is authenticated and has an affiliation
        user = self.request.user
        if user.is_authenticated and user.affiliation:
            return BrandOwner.objects.filter(id=user.affiliation.id)
        else:
            # Handle cases where the user is not affiliated with a BrandOwner
            # This could be by returning an empty queryset or handling it as per your application's logic
            return BrandOwner.objects.none()