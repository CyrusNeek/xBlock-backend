from django.db import models


class TechnicalMetaData(models.Model):
    SUCCESSFUL = "Successful"
    FAILED = "Failed"

    DATA_SYNC_STATUS_CHOICES = [
        (SUCCESSFUL, "Successful"),
        (FAILED, "Failed"),
    ]

    source_system = models.CharField(max_length=255)
    data_retrieval_created_at = models.DateTimeField(auto_now_add=True)
    data_sync_status = models.CharField(
        max_length=10, choices=DATA_SYNC_STATUS_CHOICES, default=SUCCESSFUL
    )
    api_call_id = models.TextField(null=True, blank=True)
    processing_notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Record {self.pk} from {self.source_system}"
