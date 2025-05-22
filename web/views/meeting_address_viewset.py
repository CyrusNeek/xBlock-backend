from rest_framework import viewsets
from web.models import MeetingAddress, Meeting
from web.serializers import MeetingAddressSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError


class MeetingAddressPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100 

class MeetingAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Meeting Address to be viewed or edited.
    """

    serializer_class = MeetingAddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MeetingAddressPagination

    queryset = MeetingAddress.objects.all()


    def get_queryset(self):
        """
        Returns only Meeting Address associated with meetings the user has access to.
        """
        user = self.request.user
        # accessible_meetings = Meeting.objects.accessible_by_user(user)  
        meeting_id = self.request.query_params.get('meeting_id')
        
        if not meeting_id :
            raise ValidationError({"meeting_id": "This query parameter is required."})


        accessible_meetings = (
            Meeting.objects.select_related("unit", "created_by")
            .order_by("-created_at")
            .filter(created_by=user).all()
        )

        meeting = Meeting.objects.get(pk=meeting_id)

        return MeetingAddress.objects.filter(meeting=meeting)

