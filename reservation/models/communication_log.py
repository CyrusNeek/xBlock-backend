from django.db import models


class CommunicationLog(models.Model):
    STATUS_CHOICES = [
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]

    METHOD_CHOICES = [
        ("EMAIL", "Email"),
        ("SMS", "SMS"),
        ("PHONE", "Phone"),
    ]

    COMMUNICATION_TYPE_CHOICES = [
        ("CONFIRMATION", "Confirmation"),
        ("REMINDER", "Reminder"),
    ]

    guest = models.ForeignKey(
        "Guest", on_delete=models.PROTECT, related_name="communication_log"
    )
    reservation = models.ForeignKey(
        "Reservation",
        on_delete=models.PROTECT,
        related_name="communication_log",
        null=True,
        blank=True,
    )
    communication_type = models.CharField(
        max_length=20, choices=COMMUNICATION_TYPE_CHOICES, null=True, blank=True
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Communication {self.pk} for Guest {self.guest}"
