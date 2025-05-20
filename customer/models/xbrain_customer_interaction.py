from django.db import models


class XBrainCustomerInteraction(models.Model):
    PURCHASE_ASSISTANCE = "purchase_assistance"
    SUPPORT_ASSISTANCE = "support_assistance"
    INQUIRY = "inquiry"

    INTERACTION_TYPE_CHOICES = [
        (PURCHASE_ASSISTANCE, "Purchase Assistance"),
        (SUPPORT_ASSISTANCE, "Support Assistance"),
        (INQUIRY, "Inquiry"),
    ]

    WEBSITE_CHAT = "website_chat"
    PHONE_CALL = "phone_call"
    EMAIL = "email"
    APP = "app"

    COMMUNICATION_CHANNEL_CHOICES = [
        (WEBSITE_CHAT, "Website Chat"),
        (PHONE_CALL, "Phone Call"),
        (EMAIL, "Email"),
        (APP, "App"),
    ]

    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    FAILED = "failed"

    INTERACTION_STATUS_CHOICES = [
        (COMPLETED, "Completed"),
        (IN_PROGRESS, "In Progress"),
        (ESCALATED, "Escalated"),
        (FAILED, "Failed"),
    ]

    PURCHASE_MADE = "purchase_made"
    ISSUE_RESOLVED = "issue_resolved"

    OUTCOME_CHOICES = [
        (PURCHASE_MADE, "Purchase Made"),
        (ISSUE_RESOLVED, "Issue Resolved"),
    ]

    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    interaction_date = models.DateField()
    interaction_time = models.TimeField()
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPE_CHOICES)
    channel = models.CharField(max_length=50, choices=COMMUNICATION_CHANNEL_CHOICES)
    interaction_status = models.CharField(
        max_length=50, choices=INTERACTION_STATUS_CHOICES
    )
    outcome = models.CharField(max_length=50, choices=OUTCOME_CHOICES)
    employee = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Interaction {self.pk} with {self.customer}"

    class Meta:
        db_table = "brain_customer_interaction"
        ordering = ["interaction_date", "interaction_time"]
        unique_together = (("customer", "interaction_type"),)
