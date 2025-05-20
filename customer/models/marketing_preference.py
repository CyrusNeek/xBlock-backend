from django.db import models


class MarketingPreference(models.Model):
    EMAIL = "email"
    SMS = "sms"
    PHONE_CALL = "phone_call"
    POSTAL_MAIL = "postal_mail"

    COMMUNICATION_CHANNEL_CHOICES = [
        (EMAIL, "Email"),
        (SMS, "SMS"),
        (PHONE_CALL, "Phone Call"),
        (POSTAL_MAIL, "Postal Mail"),
    ]

    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    communication_channel = models.CharField(
        max_length=50, choices=COMMUNICATION_CHANNEL_CHOICES
    )
    opt_in_status = models.BooleanField(default=False)
    opt_in_date = models.DateField(null=True, blank=True)
    opt_out_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Marketing Preference {self.pk} for {self.customer}"
