
import csv
from django.http import HttpResponse
from abc import ABC, abstractmethod

class CSVExportMixin(ABC):
    csv_filename = 'export.csv'
    csv_headers = []

    def get_csv_queryset(self):
        """
        Should return the queryset to be exported.
        """
        return self.filter_queryset(self.get_queryset())

    def get_csv_row(self, obj):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=obj)
        return [serializer.data[field] for field in self.csv_headers]

    def export_csv(self, request, *args, **kwargs):
        queryset = self.get_csv_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.csv_filename}"'

        writer = csv.writer(response)
        writer.writerow(self.csv_headers)

        for obj in queryset:
            writer.writerow(self.get_csv_row(obj))

        return response

