from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class EmotionalAnalysis(models.Model):
    EMOTION_CHOICES = [
        ("happy", "Happy"),
        ("sad", "Sad"),
        ("angry", "Angry"),
        ("neutral", "Neutral"),
    ]

    SENTIMENT_CHOICES = [
        ("positive", "Positive"),
        ("negative", "Negative"),
        ("neutral", "Neutral"),
    ]

    interaction = models.ForeignKey(
        "employee.VoiceInteraction", on_delete=models.CASCADE
    )
    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE)
    analysis_created_at = models.DateTimeField(auto_now_add=True)
    emotion = models.CharField(max_length=10, choices=EMOTION_CHOICES)
    emotion_score = models.FloatField(
        validators=[MaxValueValidator(0.0), MinValueValidator(1.0)]
    )
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    sentiment_score = models.FloatField(
        validators=[MaxValueValidator(0.0), MinValueValidator(1.0)]
    )
    additional_insights = models.CharField(max_length=255, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Analysis for {self.interaction} - {self.employee}"
