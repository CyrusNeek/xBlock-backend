from django.db import models


class ContactInformation(models.Model):
    CONTACT_TYPE_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
        ("fax", "Fax"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("verified", "Verified"),
        ("unverified", "Unverified"),
    ]

    customer = models.ForeignKey(
        "Customer", on_delete=models.PROTECT, related_name="contact_information"
    )
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPE_CHOICES)
    contact_value = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    opt_in_status = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=15, choices=VERIFICATION_STATUS_CHOICES
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"id {self.pk} : {self.contact_type} - {self.contact_value}"
