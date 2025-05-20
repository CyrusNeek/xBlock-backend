from django.db import models
from report.manager.integration_auth_manager import IntegrationAuthManager
from web.models import Unit, BlockCategory



class ToastAuth(models.Model):
    UNVERIFIED = 0
    VERIFIED = 1
    FAIL = 2
    PENDING = 3
    STATUS_CHOICES = [
        (UNVERIFIED, "Unverified"),
        (VERIFIED, "Verified"),
        (FAIL, "Fail"),
        (PENDING, "Pending"),
    ]

    unit = models.OneToOneField(
        Unit, on_delete=models.CASCADE, related_name="toast_auth"
    )
    location_id = models.CharField(max_length=200)
    username = models.CharField(max_length=300)
    host = models.CharField(max_length=500)
    block_category = models.ForeignKey(
        BlockCategory, null=True, blank=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNVERIFIED)
    error_detail = models.TextField(null=True, blank=True)
    is_initial_triggered = models.BooleanField(default=False)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    objects = IntegrationAuthManager()


    def __str__(self):
        return self.unit.name + "'s Toast Auth"
