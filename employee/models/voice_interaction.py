from django.db import models
from django.contrib.postgres.fields import ArrayField


class VoiceInteraction(models.Model):
    INTERACTION_TYPE_CHOICES = [
        ("call", "Call"),
        ("meeting", "Meeting"),
        ("training", "Training"),
    ]

    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE)
    interaction_date = models.DateField()
    interaction_time = models.TimeField()
    duration_seconds = models.PositiveIntegerField()
    interaction_type = models.CharField(max_length=15, choices=INTERACTION_TYPE_CHOICES)
    participants = ArrayField(models.CharField(max_length=100), blank=True, null=True)
    transcript = models.TextField(blank=True)
    audio_file_path = models.TextField(blank=True)
    language = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Interaction on {self.interaction_date} by {self.employee}"
