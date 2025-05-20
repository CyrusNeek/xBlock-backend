from django.db import models


class TrainingAndDevelopment(models.Model):
    TRAINING_TYPE_CHOICES = [
        ("online", "Online"),
        ("in_person", "In Person"),
        ("workshop", "Workshop"),
    ]

    COMPLETION_STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("not_started", "Not Started"),
    ]

    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE)
    training_name = models.CharField(max_length=255)
    training_type = models.CharField(
        max_length=20,
        choices=TRAINING_TYPE_CHOICES,
    )
    provider = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    completion_status = models.CharField(
        max_length=20,
        choices=COMPLETION_STATUS_CHOICES,
    )
    certification_received = models.BooleanField(default=False)
    certificate_id = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.training_name} for {self.employee}"
