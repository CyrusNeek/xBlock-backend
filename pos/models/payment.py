from django.db import models


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("cash", "Cash"),
        ("mobile_payment", "Mobile Payment"),
        ("gift_card", "Gift Card"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    ]

    transaction = models.ForeignKey("pos.Transaction", on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    amount = models.FloatField()
    payment_processor = models.CharField(max_length=100)
    card_type = models.CharField(max_length=50, blank=True, null=True)
    last_four_digits = models.CharField(max_length=4, blank=True, null=True)
    authorization_code = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50)
    payment_created_at = models.DateTimeField()
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.pk}"
