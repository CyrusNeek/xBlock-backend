from django.db import models


class Payment(models.Model):
    # PAYMENT_METHOD_CHOICES = [
    #     ("CC", "Credit Card"),
    #     ("CASH", "Cash"),
    # ]

    # PAYMENT_PROCESSOR_CHOICES = [
    #     ("STRIPE", "Stripe"),
    #     ("PAYPAL", "PayPal"),
    # ]

    reservation = models.ForeignKey(
        "Reservation", on_delete=models.PROTECT, related_name="payment"
    )
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    payment_processor = models.CharField(max_length=20, null=True, blank=True)
    deposit_amount = models.FloatField(null=True, blank=True)
    deposit_refund_status = models.CharField(max_length=255, null=True, blank=True)
    total_spend = models.FloatField(null=True, blank=True)
    bill_split_details = models.TextField(null=True, blank=True)
    transaction_created_at = models.DateTimeField(auto_now_add=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.pk} for Reservation {self.reservation}"
