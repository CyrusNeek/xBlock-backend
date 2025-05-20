from django.db import models


class CustomerSegmentation(models.Model):
    VIP = "VIP"
    NEW_CUSTOMERS = "new_customers"

    SEGMENT_NAME_CHOICES = [
        (VIP, "VIP"),
        (NEW_CUSTOMERS, "New Customers"),
    ]

    segment_name = models.CharField(max_length=50, choices=SEGMENT_NAME_CHOICES)
    description = models.TextField()
    criteria = models.CharField(max_length=255)
    notes = models.TextField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Segment {self.pk}: {self.segment_name}"
