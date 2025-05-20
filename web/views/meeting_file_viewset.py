from rest_framework import viewsets
from web.models import MeetingFile, Meeting
from web.serializers import MeetingFileSerializer, MeetingFileGetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError
from report.tasks.periodic.openai_helper import upload_file_to_open_ai


class MeetingFilePagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100 

class MeetingFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Meeting Files to be viewed or created or deleted.
    """

    serializer_class = MeetingFileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MeetingFilePagination

    queryset = MeetingFile.objects.all()

    def get_serializer_class(self):
        """
        Use CustomMeetingFileSerializer only for GET requests.
        """
        if self.request.method == 'GET':
            return MeetingFileGetSerializer
        return MeetingFileSerializer


    # def perform_create(self, serializer):
    #     file = self.request.FILES["file"]
    #     user = self.request.user 
        
    #     uploaded_file = upload_file_to_open_ai(file)
    #     if uploaded_file and uploaded_file.id:
    #         serializer.save(file_id=uploaded_file.id)


    #     serializer.save()

    def get_queryset(self):
        
        user = self.request.user
        # accessible_meetings = Meeting.objects.accessible_by_user(user)  
        meeting_id = self.request.query_params.get('meeting_id')
        
        if not meeting_id :
            raise ValidationError({"meeting_id": "This query parameter is required."})


        meeting = Meeting.objects.get(pk=meeting_id)

        return MeetingFile.objects.filter(meeting=meeting)

