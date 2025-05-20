from django.db import models
from django.db.models import Q
from roles.permissions import UserPermission
from roles.constants import LIMITED_CRUD_BLOCK_ACCESS, UNLIMITED_CRUD_BLOCK_ACCESS


class UnitManager(models.Manager):
    def accessible_by_user(self, user):
        has_limited_permission = UserPermission.check_user_permission(
            user, LIMITED_CRUD_BLOCK_ACCESS
        )
        has_unlimited_permission = UserPermission.check_user_permission(
            user, UNLIMITED_CRUD_BLOCK_ACCESS
        )

        query = Q()
        units = None

        if has_unlimited_permission:
            units = user.units.values_list("pk", flat=True)

        elif has_limited_permission:
            query |= Q(pk__in=user.brands.values_list("units", flat=True))
            query |= Q(pk__in=user.units.values_list("pk", flat=True))

        else:
            return self.get_queryset().none()

        units = self.get_queryset().filter(query) if units is None else self.get_queryset().filter(pk__in=units)

        return units


class Unit(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(
        "Brand", related_name="units", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    email = models.EmailField(blank=True)
    is_email_verified = models.BooleanField(default=False)
    website = models.URLField(blank=True)

    objects: UnitManager = UnitManager()

    vector_id = models.CharField(max_length=300, null=True, blank=True)
    order_vector_id = models.CharField(max_length=300, null=True, blank=True)
    order_items_vector_id = models.CharField(
        max_length=300, null=True, blank=True)
    toast_payment_vector_id = models.CharField(
        max_length=300, null=True, blank=True)
    toast_check_vector_id = models.CharField(
        max_length=300, null=True, blank=True)
    toast_order_vector_id = models.CharField(
        max_length=300, null=True, blank=True)
    toast_item_selection_vector_id = models.CharField(
        max_length=300, null=True, blank=True
    )
    toast_item_selection_details_vector_id = models.CharField(
        max_length=300, null=True, blank=True
    )
    resy_reservation_vector_id = models.CharField(
        max_length=300, null=True, blank=True)
    resy_rating_vector_id = models.CharField(
        max_length=300, null=True, blank=True)
    users_vector_id = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            try:
                previous = Unit.objects.get(pk=self.pk)
                if previous.email != self.email:
                    self.is_email_verified = False
                if previous.phone_number != self.phone_number:
                    self.is_phone_verified = False
            except Unit.DoesNotExist:
                pass
        else:
            self.is_email_verified = False
            self.is_phone_verified = False

        super(Unit, self).save(*args, **kwargs)
