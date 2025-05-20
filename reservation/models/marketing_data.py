from django.db import models


class MarketingData(models.Model):
    reservation = models.ForeignKey(
        "Reservation", on_delete=models.PROTECT, related_name="marketing_data"
    )
    campaign = models.CharField(max_length=255)
    discount_code = models.CharField(max_length=255, null=True, blank=True)
    referral_source = models.CharField(max_length=255)
    survey_completed = models.BooleanField(default=False)
    feedback_provided = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Marketing {self.pk} for Reservation {self.reservation}"
