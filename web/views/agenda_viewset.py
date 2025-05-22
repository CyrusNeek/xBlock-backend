from rest_framework import viewsets
from web.models import Agenda
from web.serializers import AgendaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class AgendaViewSet(viewsets.ModelViewSet):
    queryset = Agenda.objects.all()  
    serializer_class = AgendaSerializer
    permission_classes = [IsAuthenticated]  

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)  

    def get_queryset(self):
        meeting_id = self.request.query_params.get('meeting_id', None)  
        if meeting_id is not None:
            return Agenda.objects.filter(meeting__id=meeting_id)
        return Agenda.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = AgendaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AgendaSerializer(queryset, many=True)
        return Response(serializer.data)

