from django.db import models


class TradeAreaAnalysis(models.Model):
    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    home_zip_code = models.CharField(max_length=10)
    work_zip_code = models.CharField(max_length=10)
    distance_to_store = models.FloatField()
    commute_patterns = models.CharField(max_length=255)
    trade_area_latitude = models.FloatField()
    trade_area_longitude = models.FloatField()
    data_source = models.CharField(max_length=255)
    notes = models.CharField(max_length=255, null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trade Area Analysis {self.pk} for Customer {self.customer}"
