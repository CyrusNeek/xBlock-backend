from django.db import models
from subscription.models import UserSubscription
from django.conf import settings

class Invoice(models.Model):
    class ServiceChoices(models.TextChoices):
        STRIPE = 'Stripe', 'Stripe'

    service = models.CharField(
        max_length=10, 
        choices=ServiceChoices.choices,
        default=ServiceChoices.STRIPE
    )
    payload = models.TextField()
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    invoice_datetime = models.DateTimeField(null=True)
    subscription = models.OneToOneField(UserSubscription, on_delete=models.PROTECT, null=True)
    payment_status = models.CharField(max_length=255)
    customer = models.CharField(max_length=255, null=True)
    customer_email = models.CharField(max_length=255, null=True)
    customer_phone = models.CharField(max_length=255, null=True)
    invoice_pdf = models.CharField(max_length=1000, null=True)
    hosted_invoice_url = models.CharField(max_length=1000, null=True)
    number = models.CharField(max_length=255, null=True)
    period_start = models.DateTimeField(null=True)
    period_end = models.DateTimeField(null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)


    def __str__(self):
        return f"Invoice {self.pk} for {self.client.username}"