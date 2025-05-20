from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from report.models import ResyAuth
from report.models.toast_auth import ToastAuth
from report.models.tock_auth import TockAuth
from report.serializers import ResyAuthSerializer, GetResyAuthSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework import status

from report.serializers.toast_auth_serializer import ToastAuthSerializer
from report.serializers.tock_auth_serializer import TockAuthSerializer
from web.models.document import Document
from web.models.quickbooks.qb_auth_model import QuickBooksCredentials
from web.serializers.blocks.quickbooks_serializer import QuickBooksCredentialsSerializer
from web.serializers.document_serializer import DocumentSerializer

from datetime import datetime, timedelta
from django.utils.timezone import now

class IntegrationView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        query = request.query_params.get('query')
        date_filter = request.query_params.get('date')

        resy_auth_objects = ResyAuth.objects.accessible_by_user(request.user)
        resy_serializer = GetResyAuthSerializer(resy_auth_objects, many=True)
        
        toast_auth_objects = ToastAuth.objects.accessible_by_user(request.user)
        toast_serializer = ToastAuthSerializer(toast_auth_objects, many=True)
        
        tock_auth_objects = TockAuth.objects.accessible_by_user(request.user)
        tock_serializer = TockAuthSerializer(tock_auth_objects, many=True)
        
        quickbook_auth_objects = QuickBooksCredentials.objects.accessible_by_user(request.user)
        quickbook_auth_serializer = QuickBooksCredentialsSerializer(quickbook_auth_objects, many=True)
        
        
        documents_objects = Document.objects.filter(
            created_by=request.user, 
            unit_id__in=request.user.units.values_list('id', flat=True)
        )

        if query:
            documents_objects = documents_objects.filter(block_name__icontains=query)

        date_filter = request.query_params.get('date')

        if date_filter:
            try:
                start_date, end_date = find_date_range(date_filter)
                documents_objects = documents_objects.filter(created_at__gte=start_date, created_at__lte=end_date)
            except Exception as err :
                return Response({"error": str(err)}, status=400) 

        blocks_filter = request.query_params.get('blocks')  

        if blocks_filter:  
            blocks_list = blocks_filter.split(",")  
            documents_objects = documents_objects.filter(block_category__in=blocks_list)
        
        units = request.query_params.get('units')  
        if units:  
            units_list = units.split(",")  
            documents_objects = documents_objects.filter(unit__in=units_list)
        
        added_to_my_xbrain = request.query_params.get('added_to_my_xbrain')  
        if added_to_my_xbrain:  
            documents_objects = documents_objects.filter(is_added_xbrain=True)
        
        added_to_report = request.query_params.get('added_to_report')  
        if added_to_report:  
            documents_objects = documents_objects.filter(is_added_report=True)


        document_serializer = DocumentSerializer(documents_objects, many=True) 
 
        response_data = {
            "resy": resy_serializer.data,
            "toast": toast_serializer.data,
            "tock": tock_serializer.data,
            "quickbook" : quickbook_auth_serializer.data,
            "documents" : document_serializer.data
        }

        
        
        return Response(response_data, status=status.HTTP_200_OK)
    

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
