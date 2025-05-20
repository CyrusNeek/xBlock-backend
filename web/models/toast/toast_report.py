from django.db import models
from web.models import Unit
from django.db.models import JSONField  # If using Django >= 3.1 with any database


class ToastSalesSummaryReport(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='toast_sales_summary_reports')
    date = models.DateField()
    report = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.date:
            return f"Sales Report for {self.unit} dated {self.date.strftime('%Y-%m-%d')}"
        else:
            return f"Sales Report for {self.unit} on {self.updated_at.strftime('%Y-%m-%d')}"
