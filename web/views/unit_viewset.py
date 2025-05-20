from rest_framework import viewsets
from web.models import Unit
from web.serializers import UnitSerializer, UnitGetSerializer
from rest_framework.permissions import IsAuthenticated
from roles.permissions import UserPermission
from rest_framework.exceptions import PermissionDenied
from roles.constants import UNLIMITED_CRUD_TEAM_ACCESS
from rest_framework.decorators import action
from rest_framework.response import Response
from report.models import GuestProfile, ResyAuth, AnalyticReport, Tag
from vtk.models import XClassmate
from accounting.models import Team
from web.models import Unit, UnitFile, Meeting, Group, BlockCategory, User

class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UnitSerializer

    def get_serializer_class(self):
        """
        Use a different serializer class depending on the action.
        """
        if self.action in ['list', 'retrieve']:  
            return UnitGetSerializer
        return UnitSerializer 

    def get_queryset(self):
        """
        This view should return a list of all the units
        that are associated with the brands of the current user.
        """
    

        user = self.request.user
        if hasattr(user, 'brands'):  # Ensure the user has the brands attribute
            is_primary = self.request.query_params.get('isPrimary')
            if is_primary is not None:
                queryset = Unit.objects.filter(brand__in=user.brands.all(), brand__affiliation__isnull=False)
                return queryset
            else:
                return Unit.objects.filter(brand__in=user.brands.all()).distinct()
        else:
            return Unit.objects.none()
        
    def check_permission(self):
        return UserPermission.check_user_permission(self.request.user, UNLIMITED_CRUD_TEAM_ACCESS)
    
    def perform_permissions_check(self, request):
        if not self.check_permission():
            raise PermissionDenied("You don't have permission to perform this action.")
    
    def create(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        self.perform_permissions_check(request)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        unit = Unit.objects.get(id=kwargs['pk'])
        self.check_dependency_for_delete(request.user, unit )
        self.perform_permissions_check(request)
        return super().destroy(request, *args, **kwargs)

    def check_dependency_for_delete(self, user, unit: Unit):
        dependencies = {}

        # ResyAuth dependencies
        resy_auths = ResyAuth.objects.filter(unit=unit)
        if resy_auths.exists():
            dependencies['ResyAuth'] = list(resy_auths.values('id', 'email'))

        # Tag dependencies
        tags = Tag.objects.filter(unit=unit)
        if tags.exists():
            dependencies['Tag'] = list(tags.values('id', 'name'))

        # XClassmate dependencies
        # classmates = XClassmate.objects.filter(unit=unit)
        # if classmates.exists():
        #     dependencies['speech_to_knowledge'] = list(classmates.values('id', 'name'))

        # Team dependencies
        teams = unit.teams.all()
        if teams.exists():
            dependencies['Assigned to Team'] = list(teams.values('id', 'name'))

        # Meeting dependencies
        # meetings = Meeting.objects.filter(unit=unit)
        # if meetings.exists():
        #     dependencies['Meeting'] = list(meetings.values('id', 'name'))

        # Group dependencies
        # groups = Group.objects.filter(unit=unit)
        # if groups.exists():
        #     dependencies['Group'] = list(groups.values('id', 'name'))

        # BlockCategory dependencies
        categories = unit.categories.all()
        if categories.exists():
            dependencies['Assigned toBlockCategory'] = list(categories.values('id', 'name'))

        # User dependencies
        users = unit.users.all()
        if users.exists():
            dependencies['Assigned to User'] = list(users.values('id', 'full_name'))

        if dependencies:
            raise PermissionDenied({
                "message": "You cannot delete this unit because it has dependencies.",
                "dependencies": dependencies
            })

    
    
    # an custom endpoint to get just id and name
    @action(detail=False, methods=['get'])
    def listbox(self, request):
        queryset = self.get_queryset()
        data = queryset.values("id", "name")
        return Response(data)
    
