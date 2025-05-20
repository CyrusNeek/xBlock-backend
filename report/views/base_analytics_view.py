import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


from web.models import Unit
from report.models import AnalyticReport


class BaseAnalyticsView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    cronjob_function = None
    analytics_model_name = None

    status_pending_int = 3
    extra_cronjob_args = []

    def get_queryset(self):
        units = Unit.objects.accessible_by_user(self.request.user)
        return super().get_queryset().filter(unit__in=units)

    @action(detail=True, methods=["post"])
    def crawl_missing_tocks(self, request, pk=None):

        assert (
            self.cronjob_function is not None
        ), "BaseAnalyticsView must have a cronjob function defined"
        assert (
            self.analytics_model_name is not None
        ), "BaseAnalyticsView must have an analytics model name defined"

        instance = self.get_object()
        is_authorized = AnalyticReport.objects.filter(
            status=False, model_name=self.analytics_model_name, unit=instance.unit
        ).exists()

        is_initialized = AnalyticReport.objects.filter(
            model_name=self.analytics_model_name, unit=instance.unit
        ).exists()

        if (
            (is_authorized) and instance.status != self.status_pending_int
        ) or not is_initialized:
            self.cronjob_function.delay(instance.pk, *self.extra_cronjob_args)
            instance.status = self.status_pending_int
            instance.last_triggered_at = datetime.datetime.now()

            if hasattr(instance, "error_detail"):
                instance.error_detail = ""
            instance.save()
            return Response({"status": "ok"})
        if (is_authorized) and instance.status == self.status_pending_int:
            return Response({"status": "pending", "message": "Already in progress"})
        return Response({"status": "failed"})
