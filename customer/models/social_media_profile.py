from django.db import models


class SocialMediaProfile(models.Model):
    PLATFORM_CHOICES = [
        ("Facebook", "Facebook"),
        ("Twitter", "Twitter"),
        ("LinkedIn", "LinkedIn"),
        ("Instagram", "Instagram"),
    ]

    customer = models.ForeignKey(
        "Customer", on_delete=models.PROTECT, related_name="social_media_profiles"
    )
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    profile_url = models.TextField()
    username = models.CharField(max_length=100)
    is_connected = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.platform} - {self.username}"
