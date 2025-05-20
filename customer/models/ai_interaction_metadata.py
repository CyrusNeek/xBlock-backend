from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator


class AIInteractionMetadata(models.Model):
    interaction_id = models.ForeignKey(
        "customer.XBrainCustomerInteraction", on_delete=models.PROTECT
    )
    processing_time_ms = models.IntegerField(
        help_text="This field stores the processing time in milliseconds."
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    ai_model_version = models.CharField(max_length=255)
    language_model = models.CharField(max_length=255)
    error_codes = ArrayField(models.TextField(), null=True, blank=True, default=list)
    notes = models.CharField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Metadata {self.pk} for Interaction {self.interaction_id}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(confidence_score__gte=0.0)
                & models.Q(confidence_score__lte=1.0),
                name="valid_confidence_score",
            ),
        ]
