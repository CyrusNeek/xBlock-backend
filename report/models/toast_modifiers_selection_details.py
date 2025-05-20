from django.db import models
from .toast_auth import ToastAuth
from .toast_order import ToastOrder

class ToastModifiersSelectionDetails(models.Model):
    toast = models.ForeignKey(ToastAuth, on_delete=models.CASCADE)
    order = models.ForeignKey(ToastOrder, on_delete=models.CASCADE)
    sent_date = models.DateTimeField()
    order_date = models.DateTimeField()
    check_id = models.CharField(max_length=50)
    server = models.CharField(max_length=100, blank=True, null=True)
    table = models.CharField(max_length=100, blank=True, null=True)
    dining_area = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(max_length=100, blank=True, null=True)
    dining_option = models.CharField(max_length=100, blank=True, null=True)
    item_selection_id = models.CharField(max_length=50)
    modifier_id = models.CharField(max_length=50)
    master_id = models.CharField(max_length=50)
    modifier_sku = models.CharField(max_length=50, blank=True, null=True)
    modifier_plu = models.CharField(max_length=50, blank=True, null=True)
    modifier = models.CharField(max_length=200, blank=True, null=True)
    option_group_id = models.CharField(max_length=50)
    option_group_name = models.CharField(max_length=200, blank=True, null=True)
    parent_menu_selection_item_id = models.CharField(max_length=50)
    parent_menu_selection = models.CharField(max_length=200, blank=True, null=True)
    sales_category = models.CharField(max_length=200, blank=True, null=True)
    gross_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    net_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    void = models.BooleanField(default=False)
    void_reason_id = models.CharField(max_length=50, blank=True, null=True)
    void_reason = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.order.order_number} at {self.sales_category} on {self.order_date}"
