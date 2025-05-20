from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class SupportAssistantRecord(models.Model):
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    UNRESOLVED = "unresolved"

    RESOLUTION_STATUS_CHOICES = [
        (RESOLVED, "Resolved"),
        (ESCALATED, "Escalated"),
        (UNRESOLVED, "Unresolved"),
    ]

    interaction = models.ForeignKey(
        "customer.XBrainCustomerInteraction", on_delete=models.PROTECT
    )
    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    issue_reported = models.CharField(max_length=255)
    resolution_provided = models.CharField(max_length=255)
    resolution_status = models.CharField(
        max_length=50, choices=RESOLUTION_STATUS_CHOICES
    )
    escalation_ticket_id = models.ForeignKey(
        "customer.SupportTicket", null=True, blank=True, on_delete=models.SET_NULL
    )
    resolution_time = models.IntegerField()
    customer_satisfaction = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Support Record {self.pk} for {self.customer}"
