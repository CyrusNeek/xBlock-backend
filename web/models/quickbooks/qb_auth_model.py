from django.db import models

from web.models.unit import Unit
from .. import User
from web.models import BlockBase

class QuickBookManager(models.Manager):
    def accessible_by_user(self, user):
        accessible_units = Unit.objects.accessible_by_user(user)

        return self.get_queryset().filter(
            unit__in=accessible_units
        )

class QuickBooksCredentials(BlockBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=1024, null=True, blank=True)
    refresh_token = models.CharField(max_length=1024, null=True, blank=True)
    realm_id = models.CharField(max_length=256, null=True, blank=True)
    state = models.CharField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    objects = QuickBookManager()
    # def __str__(self):
    #     return self.unit.name