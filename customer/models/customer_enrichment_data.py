from django.db import models
from django.contrib.postgres.fields import ArrayField


class CustomerEnrichmentData(models.Model):
    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    additional_phones = ArrayField(
        models.CharField(max_length=15), blank=True, default=list
    )
    additional_emails = ArrayField(models.EmailField(), blank=True, default=list)
    social_media_handles = ArrayField(
        models.CharField(max_length=100), blank=True, default=list
    )
    interests = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    purchasing_behaviour = models.TextField()
    data_source = models.CharField(max_length=255)
    data_retrieval = models.DateField()
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Enrichment for Customer {self.customer}"
