from django.db import models


class PurchaseHistory(models.Model):

    COMPLETED = "completed"
    PENDING = "pending"
    REFUNDED = "refunded"
    CANCELED = "canceled"

    TRANSACTION_STATUS_CHOICES = [
        (COMPLETED, "Completed"),
        (PENDING, "Pending"),
        (REFUNDED, "Refunded"),
        (CANCELED, "Canceled"),
    ]

    customer = models.ForeignKey(
        "customer.Customer", on_delete=models.PROTECT, related_name="purchases"
    )
    order_id = models.CharField(max_length=255)
    purchase_date = models.DateField()
    purchase_time = models.TimeField()
    items_purchased = models.ForeignKey(
        "customer.ItemPurchased", on_delete=models.PROTECT, related_name="history"
    )
    total_amount = models.FloatField()
    payment_method = models.CharField(max_length=50)
    transaction_status = models.CharField(
        max_length=50,
        choices=TRANSACTION_STATUS_CHOICES,
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id}"
