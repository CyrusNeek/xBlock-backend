from rest_framework.viewsets import ModelViewSet

from report.pagination import StandardResultsSetPagination
from roles.constants import UNLIMITED_CRUD_ROLE_ACCESS
from roles.permissions import UserPermission 
from ..models import Team
from web.models import Unit
from ..serializers import TeamSerializer, TeamGetSerializer
from django.db.models import Q


class TeamView(ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.order_by('id')
    permission_classes = [UserPermission]
    pagination_class = StandardResultsSetPagination
    required_permission = UNLIMITED_CRUD_ROLE_ACCESS


    def get_queryset(self):
        """
        Return a list of all Team that the current user has permission to view.
        """
        user = self.request.user

        # return self.queryset.filter(
        #     Q(units__in=Unit.objects.accessible_by_user(user)) | Q(units__lt=1)
        # ).distinct()

        return self.queryset.filter(units__in=[user.unit])

    
    def get_serializer_class(self):
        """Use a different serializer for GET requests"""
        if self.request.method in ['GET']:
            return TeamGetSerializer  
        return TeamSerializer 

    
    
