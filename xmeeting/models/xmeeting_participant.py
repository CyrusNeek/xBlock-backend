from django.db import models
from .xmeeting import XMeeting
from .employee import Employee


class XMeetingParticipant(models.Model):
    class Meta:
        db_table = 'meeting"."xmeeting_xmeetingparticipant'


    ATTENDANCE_ATTENDED = "attended"
    ATTENDANCE_ABSENT = "absent"
    ATTENDANCE_TENTATIVE = "tentative"

    ATTENDANCE_CHOICES = [
        (ATTENDANCE_ATTENDED, "Attended"),
        (ATTENDANCE_ABSENT, "Absent"),
        (ATTENDANCE_TENTATIVE, "Tentative"),
    ]

    ROLE_ORGANIZER = "organizer"
    ROLE_PARTICIPANT = "participant"
    ROLE_SPEAKER = "speaker"

    ROLE_CHOICES = [
        (ROLE_ORGANIZER, "Organizer"),
        (ROLE_PARTICIPANT, "Participant"),
        (ROLE_SPEAKER, "Speaker"),
    ]

    xmeeting = models.ForeignKey(
        XMeeting, on_delete=models.CASCADE, related_name="participants"
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="meeting_participants"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES)
    join_time = models.DateTimeField(null=True, blank=True)
    leave_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)
    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.xmeeting.xmeeting_title} ({self.role})"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
