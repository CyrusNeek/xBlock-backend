from django.db import models


class LeadSource(models.Model):
    REFERRAL = "referral"
    ADVERTISEMENT = "advertisement"
    ORGANIC_SEARCH = "organic_search"

    SOURCE_TYPE_CHOICES = [
        (REFERRAL, "Referral"),
        (ADVERTISEMENT, "Advertisement"),
        (ORGANIC_SEARCH, "Organic Search"),
    ]

    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPE_CHOICES)
    source_details = models.CharField(max_length=255)
    acquisition_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"LeadSource {self.pk} for {self.customer}"
