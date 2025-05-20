from django.db import models
from django.utils import timezone
from web.models import Unit


class AnalyticReportManager(models.Manager):

    def create_or_override_record(
        self, date: str, status, unit, model_name, entry_count, error_detail=None
    ):
        # record = (
        #     self.get_queryset()
        #     .filter(datetime=date, unit=unit, model_name=model_name)
        #     .first()
        # )

        # if record:
        #     record.status = status
        #     record.entry_count = entry_count
        #     record.created_at = timezone.now()
        #     record.error_detail = error_detail
        #     record.save()
        #     return record

        return self.create(
            model_name=model_name,
            datetime=date,
            unit=unit,
            status=status,
            entry_count=entry_count,
            error_detail=error_detail,
            created_at=timezone.now(),
        )


class AnalyticReport(models.Model):
    model_name = models.CharField(max_length=255)
    error_detail = models.TextField(null=True, blank=True)
    entry_count = models.PositiveBigIntegerField(default=0)
    datetime = models.CharField(max_length=255)
    status = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    objects = AnalyticReportManager()
