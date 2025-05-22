from django.db import models

from web.models.brand import Brand
from .resy_auth import ResyAuth
from .report_user import ReportUser
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime


class ResyReservation(models.Model):
    resy_auth = models.ForeignKey(ResyAuth, on_delete=models.CASCADE)
    time = models.CharField(max_length=100)
    reservation_date = models.CharField(null=True, blank=True, max_length=255)
    service = models.CharField(max_length=100)
    guest = models.CharField(max_length=500)
    phone = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    party_size = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=100)
    table = models.CharField(max_length=300, null=True, blank=True)
    visit_note = models.TextField()
    reserve_number = models.CharField(max_length=300, unique=True)
    user = models.ForeignKey(ReportUser, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(
        Brand, null=True, blank=True, on_delete=models.SET_NULL)
    is_new = models.BooleanField(default=True)
    first_name = models.CharField(max_length=300, null=True, blank=True)
    last_name = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    datetime = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)
    allergy_tags = models.CharField(max_length=500, null=True, blank=True)
    guest_tags = models.CharField(max_length=500, null=True,blank=True)
    last_visit = models.DateField(null=True, blank=True)
    total_visits = models.PositiveIntegerField(null=True, blank=True)
    special_requests = models.CharField(max_length=500, null=True, blank=True)
    guest_notes = models.TextField(null=True, blank=True)
    ticket_type = models.CharField(max_length=500, null=True, blank=True)
    new_models = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.time and self.reservation_date and not self.datetime:
            datetime_str = f"{self.reservation_date} {self.time}"
            # self.datetime = make_aware(parse_datetime(datetime_str))
            self.datetime = parse_datetime(datetime_str)

        if not self.new_models:
            self.new_models = False

        super().save(*args, **kwargs)

    def can_access_block_category(self, block_category):
        try:
            return block_category.units.filter(id=self.brand.units.first().id).exists()
        except Exception as e:
            print(f"can_access_block_category Error: {e}")
            return False

    def can_access_unit(self, unit):
        try:
            if len(unit) ==1:
                res = self.brand.units.filter(id=unit.id).exists()
                return res
            else:
                res = self.brand.units.filter(id__in=unit).exists()
                return res
        except Exception as e:
            print(f"can_access_unit Error: {e}")
            return False

    class Meta:
        unique_together = ["datetime", "table", "service"]
