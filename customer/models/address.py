from django.db import models


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ("billing", "Billing"),
        ("shipping", "Shipping"),
        ("home", "Home"),
        ("work", "Work"),
    ]

    customer = models.ForeignKey(
        "Customer", on_delete=models.PROTECT, related_name="addresses"
    )
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address_type} - {self.street_address}"
