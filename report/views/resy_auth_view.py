from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from report.models import ResyAuth
from report.serializers import ResyAuthSerializer
from rest_framework.permissions import IsAuthenticated

from report.views.base_analytics_view import BaseAnalyticsView
from report.tasks.periodic.resy_crawler import get_valid_reservation_dates_and_fetch
from rest_framework.views import APIView
from rest_framework import status


class ResyAuthViewSet(BaseAnalyticsView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResyAuthSerializer
    queryset = ResyAuth.objects.all()

    cronjob_function = get_valid_reservation_dates_and_fetch
    analytics_model_name = "RESY"
    extra_cronjob_args = []


class ResyAuthUpdateView(APIView):
    permission_classes = [IsAuthenticated]  

    def patch(self, request, pk):
        try:
            resy_auth = get_object_or_404(ResyAuth, pk=pk)
        except ResyAuth.DoesNotExist:
            return Response({"error": "ResyAuth instance not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResyAuthSerializer(resy_auth, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

