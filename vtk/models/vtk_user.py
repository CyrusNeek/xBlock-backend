from django.db import models
import uuid


class VTKUser(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."stk_user'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    date_joined = models.DateField(auto_now_add=True, editable=False)
    language_preference = models.ForeignKey(
        "LanguageSupported", on_delete=models.PROTECT, related_name="user"
    )
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email}"
