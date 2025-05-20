from django.db import models


class NoteAndActivity(models.Model):
    NOTE = "Note"
    TASK = "Task"
    EVENT = "Event"

    ACTIVITY_TYPE_CHOICES = [
        (NOTE, "Note"),
        (TASK, "Task"),
        (EVENT, "Event"),
    ]

    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (CANCELED, "Canceled"),
    ]

    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    employee = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPE_CHOICES)
    activity_date = models.DateField()
    activity_time = models.TimeField()
    subject = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    notes = models.CharField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Activity {self.pk} for Customer {self.customer}"
