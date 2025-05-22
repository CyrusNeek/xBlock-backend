from rest_framework import viewsets
from roles.constants import UNLIMITED_CRUD_BRAND_ACCESS
from roles.permissions import UserPermission
from web.models import Brand
from web.serializers import SubBrandSerializer, SubBrandCreateSerializer, SubBrandObjectSerializer, SubBrandObjectUpdateSerializer

class UserSubBrandsViewSet(viewsets.ModelViewSet):
    """
    User sub brands list.
    """
    permission_classes = [UserPermission]
    required_permission = UNLIMITED_CRUD_BRAND_ACCESS
    
    def get_queryset(self):
        return Brand.objects.prefetch_related('units').filter(owner=self.request.user.affiliation).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SubBrandSerializer
        elif self.action == 'retrieve':
            return SubBrandObjectSerializer
        elif self.action == 'create':
            return SubBrandCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SubBrandObjectUpdateSerializer
        return SubBrandSerializer