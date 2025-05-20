from django.db import models
from django.contrib.postgres.fields import ArrayField


class Customer(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    loyalty_program_id = models.CharField(max_length=50, blank=True, null=True)
    loyalty_points = models.IntegerField(default=0, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    preferred_language = models.CharField(max_length=50, blank=True, null=True)
    marketing_opt_in = models.BooleanField(default=False, blank=True, null=True)
    customer_tags = ArrayField(models.CharField(max_length=50), default=list, blank=True, null=True)
    total_visits = models.PositiveIntegerField(default=0, blank=True, null=True)
    total_spend = models.PositiveIntegerField(default=0, blank=True, null=True)
    last_visit_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
