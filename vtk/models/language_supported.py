from django.db import models


class LanguageSupported(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."language_supported'

    language_code = models.CharField(
        max_length=10,
        unique=True,
    )
    language_name = models.CharField(max_length=100)
    is_supported = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def __str__(self):
        return self.language_name

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
