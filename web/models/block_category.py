from django.db import models
from enum import Enum


class BlockManager(models.Manager):
    def accessible_by_user(self, user):
        # do not change it, (circular import issue)
        from roles.constants import UNLIMITED_BLOCK_ACCESS
        from roles.permissions import UserPermission

        try:
            role = user.role
        except:
            role = None

        if role is None:
            return self.none()

        if role.is_superuser or UserPermission.user_has_permission(
            user, UNLIMITED_BLOCK_ACCESS
        ):

            return role.block_category.all()
        else:
            return user.role.block_category.all()
            # return BlockCategory.objects.filter(
            #     units__in=user.brands.values_list("units", flat=True)
            # )


class BlockCategory(models.Model):
    objects: BlockManager = BlockManager()

    class Color(Enum):
        RED = "Red"
        ORANGE = "Orange"
        YELLOW = "Yellow"
        GREEN = "Green"
        BLUE = "Blue"
        PURPLE = "Purple"
        BROWN = "Brown"
        GRAY = "Gray"
        PINK = "Pink"

    COLORS = [(color.name, color.value) for color in Color]

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50, choices=COLORS, blank=True, null=True)
    description = models.TextField(blank=True)
    units = models.ManyToManyField("Unit", blank=True, related_name="categories")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="child"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "block Categories"
