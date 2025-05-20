from django.db import models
import uuid


class GeneratedContent(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."generated_content'

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    transcription = models.ForeignKey(
        "Transcription", on_delete=models.PROTECT, related_name="generated_content"
    )
    user = models.ForeignKey(
        "VTKUser", on_delete=models.PROTECT, related_name="generated_contents"
    )
    content_type = models.ForeignKey(
        "ContentType", on_delete=models.CASCADE, related_name="generatd_contect"
    )
    language = models.ForeignKey(
        "LanguageSupported", on_delete=models.PROTECT, related_name="generated_content"
    )
    content_text = models.TextField()
    generation_date = models.DateField()
    generation_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    feedback_provided = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["generation_date"]),
            models.Index(fields=["user", "content_type", "language"]),
        ]

    def __str__(self):
        return f"Content {self.pk}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
