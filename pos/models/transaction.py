from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    ORDER_TYPE_CHOICES = [
        ("dine-in", "Dine-in"),
        ("takeout", "Takeout"),
        ("delivery", "Delivery"),
        ("online_order", "Online Order"),
        ("kiosk", "Kiosk"),
    ]

    COMPLETED = "completed"
    VOIDED = "voided"
    REFUNDED = "refunded"

    ORDER_STATUS_CHOICES = [
        (COMPLETED, "Completed"),
        (VOIDED, "Voided"),
        (REFUNDED, "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("cash", "Cash"),
        ("mobile_payment", "Mobile Payment"),
        ("gift_card", "Gift Card"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    ]

    pos_system = models.CharField(max_length=100)
    restaurant_location = models.ForeignKey(
        "pos.RestaurantLocation", on_delete=models.CASCADE
    )
    transaction_date = models.DateField()
    transaction_time = models.TimeField()
    order_type = models.CharField(max_length=50)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES)
    subtotal_amount = models.FloatField()
    tax_amount = models.FloatField()
    tip_amount = models.FloatField()
    total_amount = models.FloatField()
    discount_amount = models.FloatField()
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True
    )
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, blank=True, null=True)
    customer = models.ForeignKey("pos.Customer", on_delete=models.CASCADE)
    staff = models.ForeignKey(
        "pos.Staff", on_delete=models.CASCADE, blank=True, null=True
    )
    table_number = models.CharField(max_length=10, blank=True, null=True)
    split_payment_details = models.TextField(blank=True, null=True)
    void_reason = models.TextField(blank=True, null=True)
    refund_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    transaction_datetime = models.DateTimeField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.pk}"
