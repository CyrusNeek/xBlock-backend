from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid

from xmeeting.models.employee import Employee


class KnowledgeBase(models.Model):

    ACCESS_PUBLIC = "public"
    ACCESS_INTERNAL = "internal"
    ACCESS_RESTRICTED = "restricted"

    ACCESS_LEVEL_CHOICES = [
        (ACCESS_PUBLIC, "Public"),
        (ACCESS_INTERNAL, "Internal"),
        (ACCESS_RESTRICTED, "Restricted"),
    ]

    SOURCE_TYPE_MEETING = "meeting"
    SOURCE_TYPE_SEMINAR = "seminar"
    SOURCE_TYPE_PODCAST = "podcast"

    SOURCE_TYPE_CHOICES = [
        (SOURCE_TYPE_MEETING, "Meeting"),
        (SOURCE_TYPE_SEMINAR, "Seminar"),
        (SOURCE_TYPE_PODCAST, "Podcast"),
    ]

    source_id = models.TextField()
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    created_date = models.DateField()
    author = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="knowledge",
    )
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES)
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
