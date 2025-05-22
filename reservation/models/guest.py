from django.db import models
from django.contrib.postgres.fields import ArrayField


class Guest(models.Model):

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email_address = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    loyalty_program_id = models.CharField(max_length=255, null=True, blank=True)
    vip_status = models.BooleanField(default=False, null=True, blank=True)
    guest_notes = models.TextField(null=True, blank=True)
    guest_tags = ArrayField(
        models.CharField(max_length=255), null=True, blank=True, default=list
    )
    birthdate = models.DateField(null=True, blank=True)
    anniversary_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, null=True, blank=True, choices=GENDER_CHOICES
    )
    nationality = models.CharField(max_length=100, null=True, blank=True)
    preferred_language = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    marketing_opt_in = models.BooleanField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Guest {self.first_name} {self.last_name}"


class VisitHistory(models.Model):
    guest = models.ForeignKey(
        Guest, on_delete=models.PROTECT, related_name="visit_history"
    )
    reservation = models.ForeignKey(
        "Reservation", on_delete=models.PROTECT, related_name="visit_history"
    )
    visit_date = models.DateField()
    feedback = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Visit on {self.visit_date} for Guest {self.guest}"
