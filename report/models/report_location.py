from django.db import models
from .toast_auth import ToastAuth

class ReportLocation(models.Model):
  location = models.CharField(unique=True, max_length=500)
  toast = models.ForeignKey(ToastAuth, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  