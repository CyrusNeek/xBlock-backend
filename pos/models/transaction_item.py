from django.db import models


class TransactionItem(models.Model):
    transaction = models.ForeignKey("pos.Transaction", on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100, blank=True, null=True)
    item_sku = models.CharField(max_length=100, blank=True, null=True)
    item_category = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.FloatField()
    modifier_details = models.TextField(blank=True, null=True)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_item = models.ForeignKey("pos.Inventory", on_delete=models.CASCADE, null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.item_name} in Transaction {self.pk}"
