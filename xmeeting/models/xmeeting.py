from django.db import models
import uuid
from django.conf import settings


class XMeeting(models.Model):
    class Meta:
        db_table = 'meeting"."xmeeting_xmeeting'

    TEAM_MEETING = "team_meeting"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    PODCAST = "podcast"

    MEETING_TYPE_CHOICES = [
        (TEAM_MEETING, "Team Meeting"),
        (WORKSHOP, "Workshop"),
        (SEMINAR, "Seminar"),
        (PODCAST, "Podcast"),
    ]
    PLATFORM_ZOOM = "c"
    PLATFORM_TEAMS = "microsoft_teams"
    PLATFORM_GOOGLE_MEET = "google_meet"
    PLATFORM_WEBEX = "webex"
    PLATFORM_SKYPE = "skype"
    PLATFORM_XBLOCK = "xblock"

    PLATFORM_CHOICES = [
        (PLATFORM_ZOOM, "Zoom"),
        (PLATFORM_TEAMS, "Microsoft Teams"),
        (PLATFORM_GOOGLE_MEET, "Google Meet"),
        (PLATFORM_WEBEX, "Webex"),
        (PLATFORM_SKYPE, "Skype"),
        (PLATFORM_XBLOCK, "XBlock"),
    ]
    xmeeting_title = models.CharField(max_length=255)
    xmeeting_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    organizer = models.ForeignKey(
        "Employee", on_delete=models.PROTECT, related_name="organized_meetings"
    )
    xmeeting_type = models.CharField(max_length=30, choices=MEETING_TYPE_CHOICES)
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    location = models.TextField(help_text="Physical location or virtual xmeeting link")
    agenda = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)



    def __str__(self):
        return f"XMeeting ({self.xmeeting_title}) on {self.platform}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
