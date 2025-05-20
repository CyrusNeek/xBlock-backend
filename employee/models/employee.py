from django.db import models
from django.contrib.postgres.fields import ArrayField


class Employee(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ("active", "Active"),
        ("terminated", "Terminated"),
        ("on_leave", "On Leave"),
    ]

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    preferred_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.ForeignKey("employee.Department", on_delete=models.PROTECT, null=True, blank=True)
    manager = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    employment_status = models.CharField(
        max_length=15, choices=EMPLOYMENT_STATUS_CHOICES, default="active"
    )
    employment_start_date = models.DateField()
    employment_end_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    employee_tags = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["department", "manager"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.pk}"
