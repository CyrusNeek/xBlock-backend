from django.db import models
from report.models.report_user import ReportUser
from report.models.toast_order import ToastOrder


class ToastPayment(models.Model):
    payment_id = models.CharField(max_length=50)
    order = models.ForeignKey(ToastOrder, on_delete=models.CASCADE)
    paid_date = models.DateTimeField()
    order_date = models.DateTimeField()
    check_id = models.CharField(max_length=50)
    check_number = models.IntegerField()
    tab_name = models.CharField(max_length=200, blank=True, null=True)
    server = models.CharField(max_length=100, blank=True, null=True)
    table = models.CharField(max_length=100, blank=True, null=True)
    dining_area = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(max_length=100, blank=True, null=True)
    dining_option = models.CharField(max_length=100, blank=True, null=True)
    house_account = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tip = models.DecimalField(max_digits=10, decimal_places=2)
    gratuity = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    swiped_card_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    keyed_card_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    amount_tendered = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    refunded = models.CharField(max_length=10, blank=True, null=True)
    refund_date = models.DateTimeField(blank=True, null=True)
    refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    refund_tip_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    void_user = models.CharField(max_length=200, blank=True, null=True)
    void_approver = models.CharField(max_length=200, blank=True, null=True)
    void_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    cash_drawer = models.CharField(max_length=50, blank=True, null=True)
    card_type = models.CharField(max_length=50, blank=True, null=True)
    other_type = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(ReportUser, on_delete=models.CASCADE)

    last_4_card_digits = models.CharField(max_length=10, blank=True, null=True)
    vmcd_fees = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    room_info = models.CharField(max_length=200, blank=True, null=True)
    receipt = models.CharField(max_length=200, blank=True, null=True)
    source = models.CharField(max_length=50)
    uploaded = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment #{self.payment_id} for User #{self.user} for order ID {self.order.order_id}"
