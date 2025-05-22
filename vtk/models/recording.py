from django.db import models
import uuid


class Recording(models.Model):

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    TRANSCRIPTION_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    stk_user = models.ForeignKey(
        "VTKUser", on_delete=models.PROTECT, 
        related_name="recording",
        db_column="stk_user_id"  
    )
    recording_title = models.CharField(max_length=255)
    recording_date = models.DateField()
    recording_time = models.TimeField()
    duration_seconds = models.PositiveIntegerField()
    audio_file_path = models.TextField(blank=True, null=True)
    language = models.ForeignKey(
        "LanguageSupported", on_delete=models.PROTECT, related_name="recording"
    )
    transcription_status = models.CharField(
        max_length=50, choices=TRANSCRIPTION_STATUS_CHOICES, default=PENDING
    )
    is_uploaded = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'speech_to_knowledge"."vtk_recording'
        
        indexes = [
            models.Index(fields=["recording_date"]),
            models.Index(fields=["stk_user", "language"]),
        ]

    def __str__(self):
        return self.recording_title

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
