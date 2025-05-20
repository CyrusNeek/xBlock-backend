from django.db import models


class CustomerCommunication(models.Model):
    COMMUNICATION_TYPE_CHOICES = [
        ("email", "Email"),
        ("phone_call", "Phone Call"),
        ("sms", "SMS"),
        ("chat", "Chat"),
        ("social_media", "Social Media"),
    ]

    customer = models.ForeignKey(
        "Customer", on_delete=models.PROTECT, related_name="communications"
    )
    communication_type = models.CharField(
        max_length=20, choices=COMMUNICATION_TYPE_CHOICES
    )
    subject = models.CharField(max_length=255)
    content = models.TextField()
    communication_date = models.DateField()
    communication_time = models.TimeField()
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    channel = models.CharField(max_length=100)
    response_required = models.BooleanField(default=False)
    response_status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("responded", "Responded"),
            ("no_response_needed", "No Response Needed"),
        ],
    )
    notes = models.TextField(blank=True, null=True)
    handled_by = models.CharField(max_length=255)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.communication_type} - {self.subject}"
