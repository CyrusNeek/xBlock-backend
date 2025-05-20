from rest_framework.generics import ListAPIView
from rest_framework.viewsets import GenericViewSet
from report.models import Event
from report.pagination import StandardResultsSetPagination
from report.serializers import ReportEventSerializer
from rest_framework.permissions import IsAuthenticated
from .export_csv_view import CSVExportMixin

from rest_framework.decorators import action

class ReportEventView(ListAPIView, CSVExportMixin, GenericViewSet):
  serializer_class = ReportEventSerializer
  queryset = Event.objects.all()
  pagination_class = StandardResultsSetPagination

  permission_classes = [IsAuthenticated]

  csv_filename = 'report_events.csv'
  
  csv_headers = ['created_at', 'date', 'location', 'id', 'link', 'name']


  @action(detail=False, methods=['get'], url_path='export-csv', url_name='export_csv')
  def export_csv(self, request, *args, **kwargs):
      return super().export_csv(request, *args, **kwargs)