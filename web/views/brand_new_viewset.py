from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from roles.constants import UNLIMITED_CRUD_BRAND_ACCESS
from web.models import BrandOwner
from web.serializers import BrandSerializerNew
from web.serializers import BrandOwnerSerializerNew
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from roles.permissions import UserPermission

class UserBrandsViewSetNew(APIView):
    """
    Return the primary brand of the user.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        self.perform_permissions_check()
        return super().get_permissions()

    def perform_permissions_check(self):
        if not self.check_permission():
            raise PermissionDenied("You don't have permission to perform this action.")

    def check_permission(self):
        # Your custom permission check logic
        return UserPermission.check_user_permission(self.request.user, UNLIMITED_CRUD_BRAND_ACCESS)

    def get_object(self):
        try:
            return BrandOwner.objects.get(users=self.request.user)
        except BrandOwner.DoesNotExist:
            raise PermissionDenied("Brand owner not found.")

    def get(self, request, *args, **kwargs):
        brand_owner = self.get_object()
        serializer = BrandSerializerNew(brand_owner)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        brand_owner = self.get_object()
        serializer = BrandSerializerNew(brand_owner, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        brand_owner = self.get_object()
        serializer = BrandSerializerNew(brand_owner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandOwnerViewSetNew(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = BrandOwner.objects.all()
    serializer_class = BrandOwnerSerializerNew

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