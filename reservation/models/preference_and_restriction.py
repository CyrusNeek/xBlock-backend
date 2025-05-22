from django.db import models


class PreferenceAndRestriction(models.Model):
    guest = models.ForeignKey(
        "Guest", on_delete=models.PROTECT, related_name="guest_preference"
    )
    preference_type = models.CharField(max_length=255)
    preference_detail = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Preference {self.pk} for Guest {self.guest}"
