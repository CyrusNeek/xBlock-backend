from django.db import models
from django.conf import settings

from web.models.block_category import BlockCategory
from web.models.export_model import ExportModel
from web.models.meeting import Meeting
from web.models.unit import Unit

class DocumentManager(models.Manager):
    def accessible_by_user(self, user):
        accessible_units = Unit.objects.accessible_by_user(user)
        accessible_block_categories = BlockCategory.objects.accessible_by_user(user)

        return self.get_queryset().filter(
            unit__in=accessible_units,
            block_category__in=accessible_block_categories
        )

class Document(models.Model):
    block_name = models.CharField(max_length=100)
    unit = models.ForeignKey(
        Unit , on_delete=models.CASCADE, null=True, blank=True, related_name="unit"
    )
    block_category = models.ForeignKey(
        BlockCategory , on_delete=models.CASCADE, null=True, blank=True, related_name="block_category"
    )
    export_model = models.ForeignKey(
        ExportModel , on_delete=models.CASCADE, null=True, blank=True, related_name="documents"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    block_description = models.TextField(blank=True)

    
    is_enabled = models.BooleanField(blank=True)
    is_added_xbrain = models.BooleanField(blank=False)
    is_added_report = models.BooleanField(blank=False)

    file_id = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_documents",
    )

    diarization_text = models.TextField(blank=True)
    content = models.TextField(blank=True)

    meeting = models.ForeignKey(
        Meeting , on_delete=models.CASCADE, null=True, blank=True, related_name="meeting"
    )

    
    classmate = models.ForeignKey(
        'vtk.XClassmate',  # String reference to the model
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="classmates"
    )


    # def get_xclassmate_model(self):
    #     from vtk.models.xclassmate import XClassmate
    #     return XClassmate

    # @property
    # def xclassmate(self):
    #     XClassmate = self.get_xclassmate_model()
    #     return self.ForeignKey(
    #         XClassmate, on_delete=models.CASCADE, null=True, blank=True, related_name="classmate"
    #     )


    RECORDING_TYPE_CHOICES = [
        ("vtk", "Speech Knowledge"),
        ("meeting", "Meeting")
    ]

    
    type = models.CharField(
        max_length=20, choices=RECORDING_TYPE_CHOICES, 
        null=True , blank=True
    )
     
    objects= DocumentManager()

    def __str__(self):
        return self.block_name
    

