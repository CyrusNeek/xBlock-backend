# TODO This model implemented base on meeting and it should changed base on need models schema

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q
from roles.constants import (
    LIMITED_XCLASSMATE_ANALYTICS_ACCESS,
    UNLIMITED_XCLASSMATE_ANALYTICS_ACCESS,
)
from web.constants import WhisperLanguages
from web.models.category import Category
from web.models.unit import Unit
from roles.permissions import UserPermission


class XClassmateManager(models.Manager):
    def accessible_by_user(self, user):
        limited_xclassmate_access = UserPermission.check_user_permission(
            user, LIMITED_XCLASSMATE_ANALYTICS_ACCESS
        )
        unlimited_xclassmate_access = UserPermission.check_user_permission(
            user, UNLIMITED_XCLASSMATE_ANALYTICS_ACCESS
        )

        queryset = self.get_queryset().distinct().order_by("-created_at")

        if unlimited_xclassmate_access:
            brands = user.brands.all()
            # Get all xclassmates created by these brands
            return self.get_queryset().filter(unit__brand__in=brands)

        elif limited_xclassmate_access:
            # Get all xclassmates associated with the user's units
            user_units = user.units.all()
            return self.get_queryset().filter(unit__in=user_units)

        else:
            return queryset.filter(Q(participants=user.name) | Q(created_by=user.name))


class XClassmate(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."vtk_xclassmate'

    objects = XClassmateManager()
    created_at = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField()
    # participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Participant',
        related_name='xclassmates',
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
        related_name="created_xclassmates",
    )
    filename = models.CharField(null=True, max_length=1000)
    uploaded = models.BooleanField(default=False)
    file_id = models.CharField(max_length=255, blank=True)
    

    # source_language = models.CharField(
    # max_length=40,
    # null=True,  
    # blank=True,  
    # )

    source_language = models.CharField(
    max_length=40,
    choices=WhisperLanguages.choices(),
    default=WhisperLanguages.ENGLISH.value
    
    )

    target_language = models.CharField(
        max_length=40,
        choices=WhisperLanguages.choices(),
        default=WhisperLanguages.SPANISH.value
    )
    
    diarization_triggered = models.BooleanField(default=False)
    diarization_signal_triggered = models.BooleanField(default=False)
    diarization_id = models.IntegerField(null=True)
    report = models.TextField(null=True, blank=True)
    translated_report = models.TextField(null=True, blank=True)
    translated_summary = models.TextField(null=True, blank=True)
    new_models = models.BooleanField(default=False)

    purpose = models.TextField(null=True, blank=True)
    is_added_xbrain = models.BooleanField(default=False)
    is_added_report = models.BooleanField(default=False)
    tags = models.CharField(null=True, max_length=512)

    cover = models.URLField(max_length=1024, blank=True, null=True)
    category = models.ForeignKey(
        Category , on_delete=models.SET_NULL, null=True, blank=True, related_name="classmate_category"
    )

    sub_category = models.ForeignKey(
        Category , on_delete=models.SET_NULL, null=True, blank=True, related_name="classmate_sub_category"
    )

    full_content = models.TextField(null=True, blank=True)

    
    image_url = models.TextField(max_length=1024, null=True, blank=True)


    def __str__(self):
        return f"xclassmate on {self.created_at.strftime('%Y-%m-%d')} with {self.participants.count()} participants"

    def save(self, *args, **kwargs):
        if not self.new_models:  
            self.new_models = False
        super().save(*args, **kwargs)
