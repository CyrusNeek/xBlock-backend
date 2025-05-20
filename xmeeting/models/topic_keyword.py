from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
import uuid
from .xmeeting import XMeeting


class TopicKeyword(models.Model):
    xmeeting = models.ForeignKey(
        XMeeting, on_delete=models.CASCADE, related_name="topic_keywords"
    )
    topic_name = models.CharField(max_length=255)
    keywords = ArrayField(models.CharField(max_length=255), default=list)
    start_time = models.TimeField()
    end_time = models.TimeField()
    importance_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        
        return f"{self.topic_name} - Importance: {self.importance_score:.2f} (XMeeting: {self.xmeeting})"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
