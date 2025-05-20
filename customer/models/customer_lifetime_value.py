from django.db import models


class CustomerLifetimeValue(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    calculation_date = models.DateField()
    total_revenue = models.FloatField()
    total_cost = models.FloatField()
    clv = models.FloatField()
    clv_model = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"CLV {self.pk} for Customer {self.customer}"
