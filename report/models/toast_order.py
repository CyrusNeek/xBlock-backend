from django.db import models


from report.models.toast_auth import ToastAuth
from .report_user import ReportUser

            

class ToastOrder(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(ReportUser, on_delete=models.CASCADE, null=True, blank=True)
    is_valid = models.BooleanField(default=False)
    order_number = models.IntegerField()
    checks = models.CharField(max_length=300, null=True, blank=True)
    opened = models.DateTimeField()
    number_of_guests = models.IntegerField()
    tab_names = models.CharField(max_length=200, blank=True, null=True)
    server = models.CharField(max_length=300, blank=True, null=True)
    table = models.CharField(max_length=300, blank=True, null=True)
    revenue_center = models.CharField(max_length=300, blank=True, null=True)
    dining_area = models.CharField(max_length=300, blank=True, null=True)
    service = models.CharField(max_length=300, blank=True, null=True)
    dining_options = models.CharField(max_length=300, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    tip = models.DecimalField(max_digits=10, decimal_places=2)
    gratuity = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    voided = models.BooleanField()
    paid = models.DateTimeField(blank=True, null=True)
    closed = models.DateTimeField(blank=True, null=True)
    duration_opened_to_paid = models.CharField(max_length=20, null=True)
    order_source = models.CharField(max_length=300)
    toast_auth = models.ForeignKey(ToastAuth, on_delete=models.CASCADE)
    uploaded = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.order_number} at {str(self.user)}"

    
    class Meta:
        unique_together = ['order_id', 'order_number']
        
        
        
