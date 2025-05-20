from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import uuid
from .xmeeting import XMeeting
from .employee import Employee


class EmotionalAnalysis(models.Model):
    EMOTION_HAPPY = "happy"
    EMOTION_CONFUSED = "confused"
    EMOTION_FRUSTRATED = "frustrated"

    EMOTION_CHOICES = [
        (EMOTION_HAPPY, "Happy"),
        (EMOTION_CONFUSED, "Confused"),
        (EMOTION_FRUSTRATED, "Frustrated"),
    ]

    SENTIMENT_POSITIVE = "positive"
    SENTIMENT_NEGATIVE = "negative"
    SENTIMENT_NEUTRAL = "neutral"

    SENTIMENT_CHOICES = [
        (SENTIMENT_POSITIVE, "Positive"),
        (SENTIMENT_NEGATIVE, "Negative"),
        (SENTIMENT_NEUTRAL, "Neutral"),
    ]

    xmeeting = models.ForeignKey(
        XMeeting, on_delete=models.CASCADE, related_name="emotional_analysis"
    )
    participant = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="emotional_analysis"
    )
    created_at = models.DateTimeField()
    emotion = models.CharField(max_length=30, choices=EMOTION_CHOICES)
    emotion_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)
    sentiment_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.xmeeting} - {self.participant} - {self.emotion} ({self.created_at})"
        )

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
