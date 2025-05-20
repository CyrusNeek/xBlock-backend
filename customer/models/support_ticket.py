from django.db import models


class SupportTicket(models.Model):
    TECHNICAL = "technical"
    BILLING = "billing"
    GENERAL = "general"

    ISSUE_TYPE_CHOICES = [
        (TECHNICAL, "Technical"),
        (BILLING, "Billing"),
        (GENERAL, "General"),
    ]

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    TICKET_STATUS_CHOICES = [
        (OPEN, "Open"),
        (IN_PROGRESS, "In Progress"),
        (RESOLVED, "Resolved"),
        (CLOSED, "Closed"),
    ]

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    PRIORITY_CHOICES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (URGENT, "Urgent"),
    ]

    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    ticket_status = models.CharField(max_length=50, choices=TICKET_STATUS_CHOICES)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    created_date = models.DateField(auto_now_add=True)
    resolved_date = models.DateField(null=True, blank=True)
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.pk}: {self.subject} - {self.ticket_status}"
