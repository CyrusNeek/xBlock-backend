from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from report.pagination import StandardResultsSetPagination
from report.serializers import AnalyticReportSerializer
from report.models import AnalyticReport
from web.models.unit import Unit


class AnalyticReportView(ListAPIView, GenericAPIView):
    serializer_class = AnalyticReportSerializer
    queryset = AnalyticReport.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        model_name = self.request.query_params.get("model_name")
        unit = self.request.query_params.get("unit")

        if not model_name or not unit:
            raise ValidationError(
                "Both 'model_name' and 'unit' parameters are required."
            )

        user = self.request.user

        if not Unit.objects.accessible_by_user(user).filter(pk=int(unit)).exists():
            raise ValidationError("You don't have permission to this unit")

        queryset = queryset.filter(model_name=model_name, unit=unit)
        return queryset
