from django.db import models
from django.db.models import Q
from roles.permissions import UserPermission
from web.models import Unit, BlockCategory
from roles.constants import LIMITED_CRUD_BLOCK_ACCESS, UNLIMITED_CRUD_BLOCK_ACCESS


class TockManager(models.Manager):
    def accessible_by_user(self, user):
        has_limited_permission = UserPermission.check_user_permission(
            user, LIMITED_CRUD_BLOCK_ACCESS
        )
        has_unlimited_permission = UserPermission.check_user_permission(
            user, UNLIMITED_CRUD_BLOCK_ACCESS
        )

        query = Q()

        if has_unlimited_permission:
            query |= Q(unit__in=user.brands.values_list("units", flat=True))

        elif has_limited_permission:
            units = list(user.units.all())
            query |= Q(unit__in=units)
        else:
            return self.get_queryset().none()

        tocks = self.get_queryset().filter(query).distinct().order_by("-created_at")

        return tocks


class TockAuth(models.Model):
    UNVERIFIED = 0
    VERIFIED = 1
    FAIL = 2
    PENDING = 3
    DISABLED_CRAWL = 4
    STATUS_CHOICES = [
        (UNVERIFIED, "Unverified"),
        (VERIFIED, "Verified"),
        (FAIL, "Fail"),
        (PENDING, "Pending"),
        (DISABLED_CRAWL, "Disabled Crawl"),
    ]

    unit = models.OneToOneField(
        Unit, on_delete=models.CASCADE, related_name="tock_auth"
    )
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNVERIFIED)
    location_id = models.CharField(null=True, blank=True)
    is_initial_triggered = models.BooleanField(default=False)
    last_previous_update = models.DateField(null=True, blank=True)
    error_detail = models.TextField(null=True, blank=True)
    block_category = models.ForeignKey(
        BlockCategory, null=True, blank=True, on_delete=models.CASCADE
    )

    objects = TockManager()

    def __str__(self):
        return self.unit.name + "'s Tock Auth"
