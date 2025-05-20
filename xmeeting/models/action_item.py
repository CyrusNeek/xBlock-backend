from django.db import models
import uuid
from .xmeeting import XMeeting
from .employee import Employee


class ActionItem(models.Model):
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_OVERDUE = "overdue"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_OVERDUE, "Overdue"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]
    xmeeting = models.ForeignKey(
        XMeeting, on_delete=models.CASCADE, related_name="action_items"
    )
    description = models.TextField()
    assigned_to = models.ForeignKey(
        Employee, on_delete=models.PROTECT, null=True, blank=True
    )
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, blank=True, null=True
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, null=True, blank=True
    )
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return f"Action Item {self.pk} - {self.description[:20]}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
