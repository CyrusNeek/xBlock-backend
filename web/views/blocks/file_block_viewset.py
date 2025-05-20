from rest_framework import viewsets

from roles.constants import LIMITED_CRUD_BLOCK_ACCESS, UNLIMITED_CRUD_BLOCK_ACCESS
from web.models.unit import Unit
from ...models import UnitFile
from ...models import FileBlock
from ...serializers import FileBlockSerializer
from rest_framework.permissions import IsAuthenticated
from roles.permissions import UserPermission
from rest_framework.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils.timezone import now

import logging

logger = logging.getLogger(__name__)

class FileBlockViewSet(viewsets.ModelViewSet):
    queryset = FileBlock.objects.all()
    serializer_class = FileBlockSerializer
    
    required_permission = [LIMITED_CRUD_BLOCK_ACCESS,UNLIMITED_CRUD_BLOCK_ACCESS]
    
    permission_classes = [IsAuthenticated, UserPermission]
    
    def get_queryset(self):
        """
        This view should return a list of all the FileBlocks
        for the currently authenticated user's unit, with filtering options.
        """
        user = self.request.user
        query_params = self.request.query_params
        files = FileBlock.objects.filter(unit__in=user.all_units).distinct()
        print(files)
        
        query = query_params.get('query')
        if query:
            files = files.filter(block_name__icontains=query)
        
        date_filter = query_params.get('date')
        if date_filter:
            try:
                start_date, end_date = find_date_range(date_filter)
                files = files.filter(created_at__gte=start_date, created_at__lte=end_date)
            except Exception as err:
                raise ValidationError({"error": str(err)})
        
        blocks_filter = query_params.get('blocks')
        if blocks_filter:
            blocks_list = blocks_filter.split(",")
            files = files.filter(category__in=blocks_list)
        
        units = query_params.get('units')
        if units:
            units_list = units.split(",")
            files = files.filter(unit__in=units_list)
        
        # added_to_my_xbrain = query_params.get('added_to_my_xbrain')
        # if added_to_my_xbrain:
        #     files = files.filter(is_added_xbrain=True)
        
        added_to_report = query_params.get('added_to_report')
        if added_to_report:
            files = files.filter(is_added_report=True)
        
        return files
    
    def perform_create(self, serializer):
        try:
            units = self.request.data.get("units", [])
            
            if isinstance(units, list) and units:
                unit_id = units[0] 

            unit = Unit.objects.filter(id=unit_id).first()
            serializer.validated_data['unit'] = unit
            file_block = serializer.save()  
            
            # Handle the many-to-many files association as before
            unit_file_ids = self.request.data.get("files", [])
            if unit_file_ids:
                unit_files = UnitFile.objects.filter(id__in=unit_file_ids)
                if unit_files.count() != len(unit_file_ids):
                    missing_ids = set(unit_file_ids) - set(unit_files.values_list('id', flat=True))
                    raise ValidationError(f"UnitFile(s) with ID(s) {missing_ids} not found.")
                file_block.files.add(*unit_files)
            
            file_block.save()
        
        except ValidationError as e:
            raise e



def find_date_range(date_filter):
    today = now()

    if date_filter == "last_day":
        start_date = today - timedelta(days=1)
        end_date = today  
    elif date_filter == "last_week":
        start_date = today - timedelta(weeks=1)
        end_date = today  
    elif date_filter == "last_month":
        start_date = today - timedelta(days=30)
        end_date = today  
    elif date_filter == "last_year":
        start_date = today - timedelta(days=365)
        end_date = today  
    else:
        raise ValueError("Invalid date filter. Use 'last_day', 'last_week', 'last_month', or 'last_year'.")
    
    return start_date, end_date

