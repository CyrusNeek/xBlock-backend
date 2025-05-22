from rest_framework.permissions import IsAuthenticated

from report.models import ToastAuth, AnalyticReport
from report.serializers import ToastAuthSerializer
from .base_analytics_view import BaseAnalyticsView
from report.tasks.periodic.toast.order_details_crawl import crawl_toast_order_details


class ToastAuthViewSet(BaseAnalyticsView):
    permission_classes = [IsAuthenticated]
    serializer_class = ToastAuthSerializer

    queryset = ToastAuth.objects.all()

    cronjob_function = crawl_toast_order_details
    analytics_model_name = "TOAST"
    extra_cronjob_args = [False]
