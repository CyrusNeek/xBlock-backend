from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid


class KnowledgeBase(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."knowledge_base'

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    APPROVAL_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]
    user = models.ForeignKey(
        "VTKUser", on_delete=models.PROTECT, related_name="knowledge_bases"
    )
    source_content = models.ForeignKey(
        "GeneratedContent", on_delete=models.CASCADE, related_name="knowledge_bases"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    language = models.ForeignKey(
        "LanguageSupported", on_delete=models.PROTECT, related_name="knowledge_base"
    )
    keywords = ArrayField(models.TextField(), default=list)
    creation_date = models.DateField()
    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES)
    approver = models.ForeignKey(
        "VTKUser", on_delete=models.PROTECT, null=True, blank=True
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
