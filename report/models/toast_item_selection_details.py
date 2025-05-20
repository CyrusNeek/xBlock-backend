from django.db import models

from .toast_auth import ToastAuth
from .toast_order import ToastOrder


class ToastItemSelectionDetails(models.Model):
    toast = models.ForeignKey(ToastAuth, on_delete=models.CASCADE)
    order = models.ForeignKey(ToastOrder, on_delete=models.CASCADE)
    uploaded = models.BooleanField(default=False)
    sent_date = models.DateTimeField(db_index=True)
    order_date = models.DateTimeField(db_index=True)
    check_id = models.CharField(max_length=50, db_index=True)
    server = models.CharField(max_length=100, blank=True, null=True)
    table = models.CharField(max_length=100, blank=True, null=True)
    dining_area = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(max_length=100, blank=True, null=True)
    dining_option = models.CharField(max_length=100, blank=True, null=True)
    item_selection_id = models.CharField(max_length=100, unique=True, db_index=True)
    item_id = models.CharField(max_length=50)
    master_id = models.CharField(max_length=50)
    sku = models.CharField(max_length=50, blank=True, null=True)
    plu = models.CharField(max_length=50, blank=True, null=True)
    menu_item = models.CharField(max_length=200, blank=True, null=True)
    menu_subgroups = models.CharField(max_length=200, blank=True, null=True)
    menu_group = models.CharField(max_length=200, blank=True, null=True)
    menu = models.CharField(max_length=200, blank=True, null=True)
    sales_category = models.CharField(max_length=200, blank=True, null=True)
    gross_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    net_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(decimal_places=2, max_digits=10)
    void = models.BooleanField(default=False)
    deferred = models.BooleanField(default=False)
    tax_exempt = models.BooleanField(default=False)
    tax_inclusion_option = models.CharField(max_length=100, blank=True, null=True)
    dining_option_tax = models.CharField(max_length=100, blank=True, null=True)
    tab_name = models.CharField(max_length=100)

    def __str__(self):
        return (
            f"Order #{self.order.order_number} at {self.menu_item} on {self.order_date}"
        )

    class Meta:
        indexes = [
            models.Index(
                fields=["sent_date", "order_date", "check_id", "item_selection_id"]
            ),
        ]
