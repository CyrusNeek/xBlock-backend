from django.db import models

from report.models.report_user import ReportUser

class ToastCheckDetails(models.Model):
    customer = models.ForeignKey(ReportUser, on_delete=models.CASCADE)

    location_code = models.CharField(max_length=50, blank=True, null=True)
    
    opened_date = models.DateField()
    opened_time = models.TimeField()
    item_description = models.TextField()
    server = models.CharField(max_length=100)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    tender = models.CharField(max_length=100)
    check_id = models.CharField(max_length=50)
    check_number = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    customer_family = models.CharField(max_length=100, blank=True, null=True)
    table_size = models.IntegerField(blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    reason_of_discount = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(max_length=200)
    uploaded = models.BooleanField(default=False)

    def __str__(self):
        return f"Check #{self.check_id} for {self.customer} at {self.location_code} on {self.opened_date}"
