from django.db import models

from report.manager.integration_auth_manager import IntegrationAuthManager
from web.models import  BlockCategory, Unit



class ResyAuth(models.Model):
    UNVERIFIED = 0
    VERIFIED = 1
    FAIL = 2
    PENDING = 3
    STATUS_CHOICES = [
        (UNVERIFIED, 'Unverified'),
        (VERIFIED, 'Verified'),
        (FAIL, 'Fail'),
        (PENDING, 'Pending'),
    ]
    
    unit = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name='resy_auth')
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNVERIFIED)
    location_id = models.CharField(null=True, blank=True)
    is_initial_triggered = models.BooleanField(default=False)
    last_previous_update = models.DateField(null=True, blank=True)
    error_detail = models.TextField(null=True, blank=True)
    block_category = models.ForeignKey(BlockCategory, null=True, blank=True, on_delete=models.CASCADE, related_name="resies_auth")
    objects = IntegrationAuthManager()

    def __str__(self):
        return self.unit.name + "'s Resy's Auth"