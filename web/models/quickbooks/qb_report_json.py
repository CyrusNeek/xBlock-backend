from django.db import models
from .. import User
from django.db.models import JSONField  # If using Django >= 3.1 with any database


class QBReportJson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance_sheet = JSONField(null=True, blank=True)

    def __str__(self):
        return f"Quickbooks Json report for {self.user.username}"
