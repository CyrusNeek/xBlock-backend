from django.db import models


class PurchaseAssistantRecord(models.Model):
    PURCHASED = "purchased"
    NOT_PURCHASED = "not_purchased"
    DECIDED = "decided"

    PURCHASE_DECISION_CHOICES = [
        (PURCHASED, "Purchased"),
        (NOT_PURCHASED, "Not Purchased"),
        (DECIDED, "Decided"),
    ]

    interaction = models.ForeignKey(
        "customer.XBrainCustomerInteraction", on_delete=models.PROTECT
    )
    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    recommendation_reason = models.CharField(max_length=255)
    purchase_decision = models.CharField(
        max_length=50, choices=PURCHASE_DECISION_CHOICES
    )
    purchase_date = models.DateField()
    purchase = models.ForeignKey(
        "customer.PurchaseHistory", on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assistant Record {self.pk} for {self.customer}"
