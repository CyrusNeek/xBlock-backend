from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from web.models import BrandOwner
from subscription.models import SubscriptionPlan
from datetime import timedelta
from django.contrib.auth import get_user_model
from multiselectfield import MultiSelectField

class UserSubscription(models.Model):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELED = 'canceled'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (CANCELED, 'Canceled'),
    ]
    
    TOCK = 'tock'
    GOOGLE_MEET = 'google_meet'
    TOAST = 'toast'
    RESY = 'resy'
    QUICK_BOOKS = 'quick_books'
    
    INTEGRATION_CHOICES = [
        (TOCK, 'Tock'),
        (GOOGLE_MEET, "Google Meet"),
        (TOAST, "Toast"),
        (RESY, "Resy"),
        (QUICK_BOOKS, "QuickBooks")
    ]

    brand_owner = models.ForeignKey(BrandOwner, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="user_subscription")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="subscriptions", null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    token_remaining = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    token_user_limit = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    total_tokens = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0, editable=False)
    meeting_remaining = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    meeting_user_limit = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    total_minutes = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0, editable=False)
    classmate_time_remaining = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    classmate_user_limit = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    total_classmate_minutes = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0, editable=False)
    upload_user_limit = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    upload_size_remaining = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    total_upload_size = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0, editable=False)
    total_integration = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    integration =  MultiSelectField(choices=INTEGRATION_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    usage_metrics = models.JSONField(null=True, blank=True)
    auto_renewal = models.BooleanField(default=False)
    last_allocation = models.DateTimeField(null=True, blank=True)
    max_sub_brand = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    max_unit_per_brand = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    email_ids = models.JSONField(blank=True, null=True, help_text="An array of email IDs")
    
    
    def save(self, *args, **kwargs):
        if not self.pk and self.start_date is None:
            self.start_date = timezone.now()

        if not self.user.is_free_trial_activated:
            self.end_date = self.start_date + timedelta(days=self.plan.free_trial_days)
        elif self.start_date:
            subscription_length_days = self.plan.subscription_length_days
            self.end_date = self.start_date + timedelta(days=subscription_length_days)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand_owner.name} - {self.plan.name}"

    class Meta:
        verbose_name = "user subscription"
        verbose_name_plural = "user subscription"