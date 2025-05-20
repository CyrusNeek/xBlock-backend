from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Transcription(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."transcription'

    class TranscriptionService(models.TextChoices):
        WHISPER = "whisper", "Whisper"
        GOOGLE_CLOUD = "google_cloud", "Google Cloud Speech-to-Text"
        MICROSOFT_AZURE = "microsoft_azure", "Microsoft Azure Speech Service"
        AMAZON_TRANSCRIBE = "amazon_transcribe", "Amazon Transcribe"
        PALM_2 = "palm_2", "PaLM 2"

    recording = models.ForeignKey(
        "Recording", on_delete=models.CASCADE, related_name="transcription"
    )
    transcription_text = models.TextField()
    language = models.ForeignKey(
        "LanguageSupported", on_delete=models.PROTECT, related_name="transcripton"
    )
    transcription_service = models.CharField(
        max_length=50,
        choices=TranscriptionService.choices,
        default=TranscriptionService.WHISPER,
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True,
        blank=True,
    )
    transcription_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Transcription Service: {self.transcription_service}, ID: {self.pk}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
