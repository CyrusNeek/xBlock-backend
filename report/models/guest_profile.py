from operator import index
from django.db import models

from web.models.brand import Brand


class Guest(models.Model):
    first_name = models.CharField(max_length=300, null=True, blank=True)
    last_name = models.CharField(max_length=300, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name='brand')
    total_visits = models.IntegerField(default=0)
    Lifetime_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    new_models = models.BooleanField(
        help_text="DO NOT CHANGE THIS FIELD AT ALL", default=False
    )

    def save(self, *args, **kwargs):
        if not self.new_models:  
            self.new_models = False
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            # Add index for object_id and toast
            models.Index(fields=['brand']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

# Match data Tock or Rest with Toast and store (GuestUser one to many with GuestProfile)
class GuestProfileManager(models.Manager):
    def filter_by_date_range(self, start_date, end_date):
        return self.filter(reservation_date__range=(start_date, end_date))
    
    def filter_by_model_name(self, model_name):
        return self.filter(model_name=model_name)
    
    def filter_by_match_status(self, match_status):
        return self.filter(matched=match_status)

    def get_resy_profiles(self, start_date=None, end_date=None):
        queryset = self.filter(model_name=GuestProfile.RESY)
        if start_date and end_date:
            queryset = queryset.filter(reservation_date__range=(start_date, end_date))
        return queryset

    def get_tock_profiles(self, start_date=None, end_date=None):
        queryset = self.filter(model_name=GuestProfile.TOCK)
        if start_date and end_date:
            queryset = queryset.filter(reservation_date__range=(start_date, end_date))
        return queryset

class GuestProfile(models.Model):
    RESY = "Resy"
    TOCK = "Tock"
    M_NEW = 1
    M_INITIAL_MATCHED = 2
    M_MATCHED = 3
    M_NOT_MATCHED = 4
    MATCH_STATUS = (
        (1, "New"),
        (2, "Inital Matched"),
        (3, "Matched"),
        (4, "Not Matched"),
    )
    user = models.ForeignKey(
        Guest, on_delete=models.CASCADE, related_name='profiles')
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    toast = models.ForeignKey(
        'ToastOrder', on_delete=models.CASCADE, related_name='guest_profiles', null=True, blank=True)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True)
    tables = models.CharField(max_length=400, blank=True, null=True)
    unit = models.ForeignKey("web.Unit", on_delete=models.SET_NULL, null=True,blank=False)
    reservation_date = models.DateTimeField(null=True)
    uploaded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    new_models = models.BooleanField(
        help_text="DO NOT CHANGE THIS FIELD AT ALL", default=False
    )
    matched = models.PositiveBigIntegerField(choices=MATCH_STATUS, default=1)

    objects = GuestProfileManager()

    def __str__(self):
        return self.user.full_name + "'s Profile"


    def save(self, *args, **kwargs):
        if not self.new_models:  
            self.new_models = False
        super().save(*args, **kwargs)

    def can_access_block_category(self, block_category):
        return block_category.can_guest_profile_access(self)


    class Meta:
        indexes = [
            # Add index for object_id and toast
            models.Index(fields=['object_id']),
            models.Index(fields=['toast']),
        ]
