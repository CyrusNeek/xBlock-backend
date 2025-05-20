from django.db import models
from django.conf import settings

from roles.constants import LIMITED_MEETING_ACCESS, UNLIMITED_MEETING_ACCESS
from web.constants import WhisperLanguages
from web.models.category import Category
from web.models.unit import Unit
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from roles.permissions import UserPermission


class MeetingManager(models.Manager):
    def accessible_by_user(self, user):
        limited_meeting_access = UserPermission.check_user_permission(
            user, LIMITED_MEETING_ACCESS
        )
        unlimited_meeting_access = UserPermission.check_user_permission(
            user, UNLIMITED_MEETING_ACCESS
        )
        
        queryset = self.get_queryset().distinct().order_by("-created_at")

        if unlimited_meeting_access:
            brands = user.brands.all()
            print("'#############")
            print(brands)
            # Get all meetings created by these brands
            return self.get_queryset().filter(unit__brand__in=brands)

        elif limited_meeting_access:
            # Get all meetings associated with the user's units
            user_units = user.units.all()
            return self.get_queryset().filter(unit__in=user_units)

        else:
            return queryset.filter(Q(participants=user.name) | Q(created_by=user.name))


class Meeting(models.Model):
    MEETING_HELD_TYPE = [
        ("In-Person", "In-Person"),
        ("Online", "Online"),
        ("Hybrid", "Hybrid")
    ]
    
    PRIVACY_LEVEL = [
        ("Public", "Public"),
        ("Internal", "Internal"),
        ("Confidential", "Confidential"),
        ("Highly-Confidential", "Highly-Confidential")
    ]

    objects = MeetingManager()
    created_at = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField()
    # participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='MeetingParticipant',
        related_name='meeting',
        blank=True,
    )

    participants_count = models.SmallIntegerField(blank=True, null=True)
    key_points = models.TextField(blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    recording_file_url = models.URLField(max_length=1024, blank=True, null=True)
    summary = ArrayField(models.TextField(), blank=True, null=True, default=list)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_meetings",
    )
    filename = models.CharField(null=True, max_length=1000)
    uploaded = models.BooleanField(default=False)
    file_id = models.CharField(max_length=255, blank=True)

    
    source_language = models.CharField(
    max_length=40,
    null=True,  
    blank=True,  
    )

    target_language = models.CharField(
        max_length=40,
        null=True,  
        blank=True, 
    )
    
    diarization_triggered = models.BooleanField(default=False)
    diarization_signal_triggered = models.BooleanField(default=False)
    diarization_id = models.IntegerField(null=True)
    report = models.TextField(null=True, blank=True)
    translated_report = models.TextField(null=True, blank=True)
    translated_summary = models.TextField(null=True, blank=True)


    purpose = models.TextField(null=True, blank=True)
    is_added_xbrain = models.BooleanField(default=False)
    is_added_report = models.BooleanField(default=False)
    tags = models.CharField(null=True, max_length=512)

    category = models.ForeignKey(
        Category , on_delete=models.SET_NULL, null=True, blank=True, related_name="meeting_category"
    )

    sub_category = models.ForeignKey(
        Category , on_delete=models.SET_NULL, null=True, blank=True, related_name="meeting_sub_category"
    )
    full_content = models.TextField(null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(null=True, max_length=20)
    repeat_period = models.IntegerField(null=True, blank=True,
        help_text="This field stores repeat perid days."
    )
    held_type = models.CharField(max_length=20, choices=MEETING_HELD_TYPE,null=True, blank=True)

    online_meeting_url = models.TextField(null=True, blank=True)
    online_meeting_platform = models.CharField(null=True, max_length=50)
    goals = models.TextField(null=True, blank=True)
    privacy_level = models.CharField(max_length=30, choices=PRIVACY_LEVEL,null=True, blank=True)


    def __str__(self):
        return f"Meeting on {self.created_at.strftime('%Y-%m-%d')} with {self.participants.count()} participants"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)