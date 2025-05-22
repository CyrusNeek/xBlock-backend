from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from web.constants import WhisperLanguages
from .xmeeting import XMeeting
import uuid


class XMeetingTranscript(models.Model):
    class Meta:
        db_table = 'meeting"."xmeeting_xmeetingtranscript'


    xmeeting = models.ForeignKey(
        XMeeting, on_delete=models.CASCADE, related_name="transcript"
    )
    transcript_text = models.TextField()
    # TODO this is whisper language and we should change it into our language model
    language = models.CharField(
        max_length=4,
        choices=WhisperLanguages.choices(),
        default=WhisperLanguages.ENGLISH.value, 
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True,
        blank=True,
    )
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Transcript for XMeeting ID {self.xmeeting.pk}: {self.language} - Confidence: {self.confidence_score}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
