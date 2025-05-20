from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from multiselectfield import MultiSelectField
from django.utils.timezone import make_aware, is_naive
from web.services.google_bucket import GoogleBucket
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


class SubscriptionPlan(models.Model):
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

    USAGE_CHOICES = [
        (DAILY, "Daily"),
        (MONTHLY, "Monthly"),
    ]

    BILLING_CHOICES = [
        (DAILY, "Daily"),
        (MONTHLY, "Monthly"),
        (QUARTERLY, "Quarterly"),
        (YEARLY, "Yearly"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    SUPPORT_LEVEL_CHOICES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("enterprise", "Enterprise"),
    ]

    TOCK = "tock"
    GOOGLE_MEET = "google_meet"
    TOAST = "toast"
    RESY = "resy"
    QUICK_BOOKS = "quick_books"

    INTEGRATION_CHOICES = [
        (TOCK, "Tock"),
        (GOOGLE_MEET, "Google Meet"),
        (TOAST, "Toast"),
        (RESY, "Resy"),
        (QUICK_BOOKS, "QuickBooks"),
    ]

    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_token_allocation = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    token_user_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    token_usage_period = models.CharField(
        max_length=10, choices=USAGE_CHOICES, blank=True, null=True
    )
    daily_token_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )
    total_meeting_duration = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    meeting_session_length = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=0,
    )
    meeting_user_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    meeting_usage_period = models.CharField(
        max_length=10, choices=USAGE_CHOICES, blank=True, null=True
    )
    daily_meeting_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )
    # total_classmate_duration = models.PositiveIntegerField(
    #     validators=[MinValueValidator(0)], default=0
    # )
    total_classmate_session_duration = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], default=0
    )
    classmate_user_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    classmate_usage_period = models.CharField(
        max_length=10, choices=USAGE_CHOICES, blank=True, null=True
    )
    stk_session_length = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], default=0
    )
    daily_stk_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], null=True, blank=True
    )
    total_upload_allocation = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=1,
        help_text="MB",
    )
    upload_user_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    upload_usage_period = models.CharField(
        max_length=10, choices=USAGE_CHOICES, blank=True, null=True
    )
    daily_upload_limit = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="MB",
    )
    subscription_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    total_integration = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], default=0
    )
    integration = MultiSelectField(choices=INTEGRATION_CHOICES, null=True, blank=True)
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    flat_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES)
    subscription_length_days = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    support_level = models.CharField(max_length=10, choices=SUPPORT_LEVEL_CHOICES)
    features_included = models.TextField(null=True, blank=True)
    is_primary = models.BooleanField(default=True)
    payment_url = models.TextField(null=True)
    max_sub_brand = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    max_unit_per_brand = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    image = models.ImageField(upload_to="subscription_plan/", null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)

    stripe_id = models.CharField(max_length=100)

    free_trial_days = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)]
    )


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.start_time and is_naive(self.start_time):
            self.start_time = make_aware(self.start_time)
        if self.end_time and is_naive(self.end_time):
            self.end_time = make_aware(self.end_time)
        if self.image:

            path = f"temporary_uploads/subscription_plan/{self.name}-{self.image.name}"
            full_path = default_storage.save(path, ContentFile(self.image.read()))

            local_path = default_storage.path(full_path)

            google_bucket = GoogleBucket()
            destination = f"subscription_plan_images/{self.name}-{self.image.name}"
            google_bucket.upload_or_replace(local_path, destination)

            public_url = google_bucket.generate_presigned_download_url(
                destination, None
            )[0]
            self.image_url = public_url

        super().save(*args, **kwargs)
