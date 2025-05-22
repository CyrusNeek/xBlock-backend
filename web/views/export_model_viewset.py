from rest_framework import viewsets
from web.models import ExportModel
from web.models.document import Document
from web.models.meeting import Meeting
from web.serializers import ExportModelSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from web.serializers.document_serializer import DocumentSerializer


class ExportModelViewSet(APIView):
    permission_classes = [IsAuthenticated]

    queryset = ExportModel.objects.all()
    serializer_class = ExportModelSerializer

    def get(self, request, category_id=None, *args, **kwargs):
        filter_params = {
                'is_enabled': True,
                'parent__isnull': True,
            }
        
        export_model_type = request.query_params.get('type', None)
        if export_model_type:
                filter_params['type'] = export_model_type

        export_models = ExportModel.objects.filter(**filter_params)
        serializer = ExportModelSerializer(export_models, many=True, context={'request': request})
    
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ExportModelListView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        meeting_id = request.query_params.get('meeting_id')
        raise NotImplementedError("This feature is not implemented yet." )
        
        if not meeting_id:
            return Response({"error": "meeting_id is required"}, status=400)
        
