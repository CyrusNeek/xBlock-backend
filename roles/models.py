from django.db import models
from web.models.brand_owner import BrandOwner


class PermissionCategory(models.Model):
    label = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    group_type = models.CharField(
        max_length=50, choices=[("FAL", "Features Access Level")], default="FAL"
    )
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "permission category"
        verbose_name_plural = "permission categories"


class Permission(models.Model):
    component_key = models.CharField(max_length=255, blank=True, unique=True)
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        PermissionCategory, on_delete=models.RESTRICT, related_name="child"
    )
    dependent_permission = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="depends_on"
    )
    excludes = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="excluded_by"
    )
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.label


class Role(models.Model):
    brand_owner = models.ForeignKey(BrandOwner, on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    key_code = models.CharField(max_length=100, null=True, blank=True)
    creator = models.ForeignKey(
        "web.User",
        on_delete=models.SET_NULL,
        related_name="role_manager",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    permissions = models.ManyToManyField(Permission)
    is_superuser = models.BooleanField(default=False)
    is_immuteable = models.BooleanField(default=False, null=True, blank=True) # == if true is superAdmin and not possible to Delete 
    block_category = models.ManyToManyField(
        "web.BlockCategory", related_name="roles", blank=True
    )

    def __str__(self):
        return self.label
