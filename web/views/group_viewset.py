from rest_framework import viewsets
from ..models import Group
from ..serializers import GroupSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        # Set the unit of the group to be the same as the request user's unit
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save(unit=request.user.unit)

        # Add the request user to the group's users
        group.users.add(request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
        
    def get_queryset(self):
        """
        This view should return a list of all the groups
        that are owned by the currently authenticated user.
        """
        user = self.request.user
        return Group.objects.filter(unit=user.unit)
