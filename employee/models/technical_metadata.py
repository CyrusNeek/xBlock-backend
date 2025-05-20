from django.db import models


class TechnicalMetaData(models.Model):
    source_system = models.CharField(max_length=255)
    data_retrieval_created_at = models.DateTimeField(auto_now_add=True)
    data_sync_status = models.CharField(
        max_length=10, choices=[("Successful", "successful"), ("Failed", "failed")]
    )
    api_call = models.TextField()
    processing_notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Record {self.pk} from {self.source_system} - Status: {self.data_sync_status}"
