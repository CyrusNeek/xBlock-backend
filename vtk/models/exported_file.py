from django.db import models
import uuid


class ExportedFile(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."exported_file'

    PDF = "pdf"
    EXCEL = "excel"
    DOCS = "docs"

    FILE_FORMAT_CHOICES = [(PDF, "Pdf"), (EXCEL, "Excel"), (DOCS, "Docs")]

    content = models.ForeignKey(
        "GeneratedContent", on_delete=models.PROTECT, related_name="exported_files"
    )
    user = models.ForeignKey(
        "VTKUser", on_delete=models.PROTECT, related_name="exported_files"
    )
    export_date = models.DateField()
    export_time = models.TimeField()
    file_format = models.CharField(max_length=15, choices=FILE_FORMAT_CHOICES)
    file_path = models.TextField()
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return f"File {self.pk}"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
