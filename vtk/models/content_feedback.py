import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ContentFeedback(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."content_feedback'

    content = models.ForeignKey(
        "GeneratedContent", on_delete=models.CASCADE, related_name="feedbacks"
    )
    user = models.ForeignKey(
        "VTKUser", on_delete=models.PROTECT, related_name="content_feedbacks"
    )
    feedback_date = models.DateField()
    feedback_time = models.TimeField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )
    comments = models.TextField(blank=True, null=True)
    improvement_suggestions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback {self.pk}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
