from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator


class XBrainConversationLog(models.Model):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

    SENTIMENT_CHOICES = [
        (POSITIVE, "Positive"),
        (NEUTRAL, "Neutral"),
        (NEGATIVE, "Negative"),
    ]

    interaction = models.ForeignKey(
        "customer.XBrainCustomerInteraction", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(
        max_length=255, choices=[("customer", "Customer"), ("xbrain", "XBrain")]
    )
    message = models.TextField()
    language = models.CharField(max_length=50)
    sentiment = models.CharField(max_length=50, choices=SENTIMENT_CHOICES)
    sentiment_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    intent = models.CharField(max_length=255)
    entities = ArrayField(models.TextField(), blank=True, null=True, default=list)
    notes = models.CharField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(sentiment_score__gte=0.0)
                & models.Q(sentiment_score__lte=1.0),
                name="valid_sentiment_score",
            ),
        ]

    def __str__(self):
        return f"Conversation {self.pk} - {self.language} - {self.sentiment}"
