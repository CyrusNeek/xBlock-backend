from django.db import models

from .toast_auth import ToastAuth


class ToastTimeEntries(models.Model):
    toast = models.ForeignKey(ToastAuth, on_delete=models.CASCADE)

    time_entry_id = models.CharField(max_length=200, unique=True)
    guid = models.CharField(max_length=100, null=True)
    employee_id = models.CharField(max_length=50)
    employee_guid = models.CharField(max_length=100)
    employee_external_id = models.CharField(max_length=50, blank=True, null=True)
    employee = models.CharField(max_length=200)
    job_id = models.CharField(max_length=50)
    job_guid = models.CharField(max_length=100)
    job_code = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.CharField(max_length=200, blank=True, null=True)
    in_date = models.DateTimeField()
    out_date = models.DateTimeField()
    auto_clock_out = models.BooleanField(default=False)
    total_hours = models.DecimalField(max_digits=10, decimal_places=2)
    unpaid_break_time = models.DecimalField(max_digits=10, decimal_places=2)
    paid_break_time = models.DecimalField(max_digits=10, decimal_places=2)
    payable_hours = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    cash_tips_declared = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    non_cash_tips = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    total_gratuity = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    total_tips = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    tips_withheld = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    wage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    regular_hours = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_hours = models.DecimalField(max_digits=10, decimal_places=2)
    regular_pay = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    overtime_pay = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total_pay = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"Time Entry #{self.id} at {self.location} by {self.employee} on {self.in_date.date()}"
