from django.db import models


class TechnicalMetadata(models.Model):
    DATA_SYNC_STATUS_CHOICES = [
        ("SUCCESS", "Successful"),
        ("FAILED", "Failed"),
    ]

    reservation = models.ForeignKey(
        "Reservation", on_delete=models.PROTECT, related_name="technical_metadata"
    )
    api_call = models.CharField(max_length=255, null=True, blank=True)
    data_source = models.CharField(max_length=255)
    data_sync_status = models.CharField(
        max_length=255,
        choices=DATA_SYNC_STATUS_CHOICES,
        null=True,
        blank=True,
    )
    data_retrieval_created_at = models.DateTimeField()
    processing_notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Technical Metadata {self.pk} for Reservation {self.reservation}"
