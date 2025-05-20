from django.db import models


class Customer(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    ACTIVE= "active"
    INACTIVE= "inactive"
    PROSPECT = "prospect"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
        (PROSPECT, "Prospect"),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    preferred_language = models.CharField(max_length=50, null=True, blank=True)
    customer_since = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    segment_id = models.ForeignKey("CustomerSegmentation", on_delete=models.PROTECT, null=True, blank=True)
    loyalty_program_id = models.ForeignKey("LoyaltyProgram", on_delete=models.PROTECT, null=True, blank=True)
    lifetime_value = models.FloatField()
    notes = models.TextField(null=True, blank=True)
    ai_interaction_consent = models.BooleanField(default=False)
    data_enriched = models.BooleanField()
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
