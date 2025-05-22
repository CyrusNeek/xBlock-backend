from rest_framework import viewsets
from vtk.models import Participant, XClassmate
from vtk.serializers import ParticipantSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError


class XClassmateParticipantPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100 

class ParticipantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows XClassmate Participants to be viewed or edited.
    """

    serializer_class = ParticipantSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = XClassmateParticipantPagination

    queryset = Participant.objects.all()


    def get_queryset(self):
        """
        Returns only XClassmate Participants associated with meetings the user has access to.
        """
        print("======called ======")
        user = self.request.user
        # accessible_meetings = XClassmate.objects.accessible_by_user(user)  
        classmate_id = self.request.query_params.get('xclassmate_id')
        
        if not classmate_id :
            raise ValidationError({"classmate_id": "This query parameter is required."})


       

        classmate = XClassmate.objects.get(pk=classmate_id)

        return Participant.objects.filter(xclassmate=classmate)

