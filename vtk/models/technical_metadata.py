from django.db import models
import uuid


class TechnicalMetadata(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."technical_metadata'

    TRANSCRIPTION = "transcription"
    CONTENT_GENERATION = "content_generation"

    PROCESS_NAME_CHOICES = [
        (TRANSCRIPTION, "Transcription"),
        (CONTENT_GENERATION, "Content Generation"),
    ]

    SUCCESSFUL = "successful"
    FAILED = "failed"

    STATUS_CHOICES = [
        (SUCCESSFUL, "Successful"),
        (FAILED, "Failed"),
    ]
    process_name = models.CharField(max_length=30, choices=PROCESS_NAME_CHOICES)
    source_id = models.CharField(max_length=36)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )
    created_at = models.DateTimeField()
    error_message = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return f"Metadata {self.pk}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
