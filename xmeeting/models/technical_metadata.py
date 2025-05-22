from django.db import models
import uuid


class TechnicalMetadata(models.Model):

    DATA_SYNC_SUCCESSFUL = "successful"
    DATA_SYNC_FAILED = "failed"

    DATA_SYNC_STATUS_CHOICES = [
        (DATA_SYNC_SUCCESSFUL, "Successful"),
        (DATA_SYNC_FAILED, "Failed"),
    ]

    source_system = models.CharField(max_length=255)
    data_retrieval_created_at = models.DateTimeField()
    data_sync_status = models.CharField(max_length=20, choices=DATA_SYNC_STATUS_CHOICES)
    api_call_id = models.TextField(blank=True, null=True)
    processing_notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.source_system} - {self.data_sync_status} ({self.data_retrieval_created_at})"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
