from rest_framework import viewsets, status
from django.db.models import Count, Q
from roles.constants import UNLIMITED_CRUD_ROLE_ACCESS
from web.models.unit import Unit
from ..models import BlockCategory
from ..serializers import BlockCategorySerializer
from roles.permissions import UserPermission
from rest_framework.response import Response
from report.pagination import StandardResultsSetPagination
from roles.models import Role

class BlockCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [UserPermission]
    pagination_class = StandardResultsSetPagination
    required_permission = UNLIMITED_CRUD_ROLE_ACCESS
    queryset = (
        BlockCategory.objects.annotate(
            block_count=Count("fileblock", distinct=True)
            + Count("urlblock", distinct=True)
        )
        .order_by('id')
    )
    serializer_class = BlockCategorySerializer

    def get_queryset(self):
        """
        Return a list of all BlockCategory that the current user has permission to view.
        """
        user = self.request.user

        # return self.queryset.filter(
        #     Q(units__in=Unit.objects.accessible_by_user(user)) | Q(units__lt=1)
        # )
        return self.queryset.filter(units__in=[user.unit])

    def create(self, request, *args, **kwargs):
        user = request.user
        # units = Unit.objects.accessible_by_user(user)

        # if units.exists() is False:
        #     return Response(
        #         {"detail": "User has no associated units."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # data = request.data.copy()

        # if data.get("unit") and data["unit"] not in units.values_list("pk", flat=True):
        #     return Response(
        #         {"detail": "This unit is not permitted for you."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # block_category = self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        block_category = serializer.save()
        assign_block_category_to_super_admin(user, block_category)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
    
def assign_block_category_to_super_admin(user, block_category):
    try:
        super_admin_role = Role.objects.get(brand_owner=user.affiliation, is_immuteable=True)
        super_admin_role.block_category.add(block_category)  
        super_admin_role.save()
    except Role.DoesNotExist:
        print("Super admin role does not exist for this brand owner.")
# user --> affiliation --> brand owner --> role --> is immutable and 