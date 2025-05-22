from django.db import models


class ItemPurchased(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.FloatField()
    total_price = models.FloatField()
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
