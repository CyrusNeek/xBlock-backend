from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from report.models import TockAuth
from report.models.analytic_report import AnalyticReport
from report.serializers import TockAuthSerializer
from report.tasks.periodic.tock_crawler import crawl_tock_from_past


class TockAuthViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TockAuthSerializer

    def get_queryset(self):
        return TockAuth.objects.accessible_by_user(self.request.user)

    @action(detail=True, methods=["post"])
    def crawl_missing_tocks(self, request, pk=None):
        tock_auth: TockAuth = self.get_object()
        is_authorized = AnalyticReport.objects.filter(
            status=False, model_name="TOCK", unit=tock_auth.unit
        ).exists()

        is_initialized = AnalyticReport.objects.filter(
            model_name="TOCK", unit=tock_auth.unit
        ).exists()

        if (
            (is_authorized) and tock_auth.status != TockAuth.PENDING
        ) or not is_initialized:
            crawl_tock_from_past.delay(tock_auth.pk)
            tock_auth.status = TockAuth.PENDING
            tock_auth.error_detail = ""
            tock_auth.save()
            return Response({"status": "ok"})

        return Response({"status": "failed"})
