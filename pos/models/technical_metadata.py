from django.db import models


class TechnicalMetadata(models.Model):
    DATA_SYNC_STATUS_CHOICES = [
        ("successful", "Successful"),
        ("failed", "Failed"),
    ]

    source_system = models.CharField(max_length=100)
    data_retrieval_created_at = models.DateTimeField(auto_now_add=True)
    data_sync_status = models.CharField(max_length=50, choices=DATA_SYNC_STATUS_CHOICES)
    api_call = models.TextField(blank=True, null=True)
    processing_notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Record {self.pk}"
