from django.db import models

from .toast_auth import ToastAuth


class ToastCashTransaction(models.Model):
    toast = models.ForeignKey(ToastAuth, on_delete=models.CASCADE)
    entry_id = models.CharField(max_length=50)
    created_date = models.DateTimeField(null=True, blank=True)
    action = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    cash_drawer = models.CharField(max_length=50)
    payout_reason = models.CharField(max_length=100, blank=True, null=True)
    no_sale_reason = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    employee = models.CharField(max_length=100)
    employee_2 = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Transaction #{self.entry_id} at {self.toast}"
