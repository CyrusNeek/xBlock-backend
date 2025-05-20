from django.db import models


class Inventory(models.Model):
    item_name = models.CharField(max_length=100)
    item_sku = models.CharField(max_length=100)
    item_category = models.CharField(max_length=100)
    current_stock_level = models.IntegerField()
    reorder_level = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_id = models.CharField(max_length=50, blank=True, null=True)
    last_restock_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name
