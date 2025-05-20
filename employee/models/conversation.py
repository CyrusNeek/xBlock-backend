from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField


class Conversation(models.Model):
    EMAIL = "email"
    CHAT = "chat"
    FORUM = "forum"

    CONVERSATION_TYPE_CHOICES = [
        (EMAIL, "Email"),
        (CHAT, "Chat"),
        (FORUM, "Forum"),
    ]

    SENTIMENT_CHOICES = [
        ("positive", "Positive"),
        ("negative", "Negative"),
        ("neutral", "Neutral"),
    ]

    employee = models.ForeignKey(
        "employee.Employee", on_delete=models.PROTECT, related_name="conversation"
    )
    conversation_date = models.DateField()
    conversation_time = models.TimeField()
    conversation_type = models.CharField(
        max_length=20, choices=CONVERSATION_TYPE_CHOICES
    )
    participants = ArrayField(
        models.CharField(max_length=255), default=list, blank=True, null=True
    )
    content = models.JSONField(default=dict)
    language = models.CharField(max_length=255)
    sentiment = models.CharField(
        max_length=15, choices=SENTIMENT_CHOICES, blank=True, null=True
    )
    sentiment_score = models.FloatField(
        validators=[MaxValueValidator(1.0), MinValueValidator(0.0)],
        blank=True,
        null=True,
    )
    topics = ArrayField(
        models.CharField(max_length=255), default=list, blank=True, null=True
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Conversation {self.pk} with {self.employee} on {self.conversation_date}"
        )
