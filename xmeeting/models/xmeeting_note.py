import uuid
from django.db import models
from .xmeeting import XMeeting
from .employee import Employee


class XMeetingNote(models.Model):
    VISIBILITY_PRIVATE = "private"
    VISIBILITY_TEAM = "team"
    VISIBILITY_PUBLIC = "public"

    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE, "Private"),
        (VISIBILITY_TEAM, "Team"),
        (VISIBILITY_PUBLIC, "Public"),
    ]
    xmeeting = models.ForeignKey(
        XMeeting, on_delete=models.CASCADE, related_name="note"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="meeting_note"
    )
    note_text = models.TextField()
    created_at = models.DateTimeField()
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES)
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return f"Note for XMeeting {self.xmeeting.pk} - Visibility: {self.visibility}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
