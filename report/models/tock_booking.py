from enum import Enum
from django.db import models

from web.models.brand import Brand
from .tag import Tag
from .report_user import ReportUser


class TockBooking(models.Model):
    class BookStatus(Enum):
        AVAILABLE = "Available"
        CANCELED = "Canceled"
        BOOKED = "Booked"
        NO_SHOW = "No Show"

    STATUSES = [(status.name, status.value) for status in BookStatus]

    report_triggered_at = models.DateTimeField(auto_now=True)
    tock = models.ForeignKey(
        "TockAuth", on_delete=models.CASCADE, null=True, blank=True
    )

    time = models.DateTimeField(null=True)
    status = models.CharField(max_length=15, choices=STATUSES)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    party_size = models.PositiveIntegerField()
    booking_owner = models.CharField(max_length=200)
    user = models.ForeignKey(
        ReportUser, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(
        Brand, null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=300, null=True, blank=True)
    last_name = models.CharField(max_length=300, null=True, blank=True)
    experience = models.CharField(max_length=400, blank=True)
    price_per_person = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    supplements = models.CharField(max_length=400, blank=True)
    question_answers = models.TextField(blank=True)
    visit_notes = models.TextField(blank=True)
    visit_dietary_notes = models.TextField(blank=True)
    guest_provided_order_notes = models.TextField(blank=True)
    guest_notes = models.TextField(blank=True)
    dietary_notes = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name="articles")
    phone = models.CharField(max_length=200, null=True, blank=True)
    is_new = models.BooleanField(default=True)
    guest_tags = models.ManyToManyField(Tag, related_name="guest_articles")

    visit_tags = models.ManyToManyField(Tag, related_name="visit_articles")
    email = models.EmailField(max_length=100, null=True, blank=True)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, null=True, blank=True
    )
    gross_amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, null=True, blank=True
    )
    net_amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, null=True, blank=True
    )
    service_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, null=True, blank=True
    )
    gratuity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, null=True
    )
    confirmation = models.CharField(max_length=100, blank=True)
    visits = models.PositiveIntegerField(default=0, null=True, blank=True)
    last_visit_date = models.DateField(null=True, blank=True)
    last_visit_time = models.TimeField(null=True, blank=True)
    group_visits = models.PositiveIntegerField(
        default=0, null=True, blank=True)
    last_group_visit_date = models.DateField(null=True, blank=True)
    last_group_visit_time = models.TimeField(null=True, blank=True)
    last_group_visit_restaurant = models.CharField(max_length=100, blank=True)
    spouse_name = models.CharField(max_length=400, blank=True)
    birthday = models.DateField(null=True, blank=True)
    booking_method = models.CharField(max_length=100, blank=True)
    modified_by = models.CharField(max_length=400, blank=True)
    final_status = models.CharField(max_length=100, blank=True)
    tables = models.CharField(max_length=400, blank=True)
    servers = models.CharField(max_length=400, blank=True)
    dining_time_seconds = models.PositiveIntegerField(default=0, null=True)
    uploaded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} | {self.birthday}"

    def can_access_block_category(self, block_category):
        try:
            return block_category.units.filter(id=self.brand.units.first().id).exists()
        except Exception as e:
            print(f"can_access_block_category Error: {e}")
            return False

    def can_access_unit(self, unit):
        try:
            if len(unit) == 1:
                return self.brand.units.filter(id=unit.id).exists()
            else:
                return self.brand.unit.filter(id__in=unit).exists()
        except Exception as e:
            print(f"can_access_unit Error: {e}")
            return False

    class Meta:
        unique_together = ("time", "confirmation")
