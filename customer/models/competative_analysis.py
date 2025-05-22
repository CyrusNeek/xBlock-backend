from django.db import models


class CompetitiveAnalysis(models.Model):
    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    competitor = models.CharField(max_length=255)
    competitor_name = models.CharField(max_length=255)
    visit_date = models.DateField()
    visit_time = models.TimeField()
    visit_frequency = models.IntegerField()
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Analysis {self.pk} for Customer {self.customer}"
