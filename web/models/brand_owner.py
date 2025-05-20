from django.db import models
import pytz


class BrandOwner(models.Model):
    STATE_CHOICES = [
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DE", "Delaware"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MD", "Maryland"),
        ("MA", "Massachusetts"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VT", "Vermont"),
        ("VA", "Virginia"),
        ("WA", "Washington"),
        ("WV", "West Virginia"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming"),
    ]

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    public_business_name = models.CharField(max_length=30, blank=True)
    website = models.CharField(max_length=300, blank=True)
    email = models.EmailField(blank=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    account_name = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=50, blank=True)
    address2 = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True)
    city = models.CharField(max_length=20, blank=True)
    brand_owner_image_url = models.TextField(null=True, blank=True)

    workspace_type = models.CharField(max_length=100, null=True, blank=True)

    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default="America/Chicago",
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Brand Owner"
        verbose_name_plural = "Brand Owners"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            try:
                previous = BrandOwner.objects.get(pk=self.pk)
                if previous.email != self.email:
                    self.is_email_verified = False
                if previous.phone_number != self.phone_number:
                    self.is_phone_verified = False
            except BrandOwner.DoesNotExist:
                pass
        else:
            self.is_email_verified = False
            self.is_phone_verified = False

        super(BrandOwner, self).save(*args, **kwargs)