from django.db import models

from web.models import Unit


class OpenAIFile(models.Model):
    class CategoryChoices(models.TextChoices):
        TOCK = 'tock', 'Tock'
        RESY_RESERVATION = 'resy', 'ResyReservation'
        TOAST_ITEMS = 'items', 'ToastItems'
        TOAST = 'toast', 'Toast'
        MEETING = 'meeting', 'Meeting'
        PAYMENTS = 'payments', 'Payments'
        USERS = 'users', 'Users'
        UNITFILE_NAME = 'unit-file', 'unit-file'

    file_name = models.CharField(max_length=255)
    file_id = models.CharField(max_length=255)
    # file_url = models.URLField(max_length=255)
    block_category = models.ForeignKey('BlockCategory', null=True, blank=True, on_delete=models.SET_NULL, related_name="openai_files")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    model_name = models.TextField(choices=CategoryChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.unit} - {self.file_name}"
