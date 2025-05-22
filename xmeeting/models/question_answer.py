from django.db import models
from .xmeeting import XMeeting
from .employee import Employee
import uuid


class QuestionAnswer(models.Model):
    xmeeting = models.ForeignKey(XMeeting, on_delete=models.CASCADE, related_name="qa")
    question = models.TextField()
    answer = models.TextField()
    asked_by = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="questions"
    )
    answered_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="answers",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField()
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return f"Question: {self.question} | XMeeting: {self.xmeeting.xmeeting_title}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
