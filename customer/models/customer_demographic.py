from django.db import models


class CustomerDemographic(models.Model):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
    ]

    LESS_THAN_50K = "<50K"
    BETWEEN_50K_AND_100K = "50K - 100K"
    GREATER_THAN_100K = ">100K"

    INCOME_RANGE_CHOICES = [
        (LESS_THAN_50K, "<50K"),
        (BETWEEN_50K_AND_100K, "50K - 100K"),
        (GREATER_THAN_100K, ">100K"),
    ]

    SINGLE = "single"
    MARRIED = "married"

    MARITAL_STATUS_CHOICES = [
        (SINGLE, "Single"),
        (MARRIED, "Married"),
    ]

    OWNER = "owner"
    RENTER = "renter"

    HOMEOWNER_STATUS_CHOICES = [
        (OWNER, "Owner"),
        (RENTER, "Renter"),
    ]
    customer = models.ForeignKey("customer.Customer", on_delete=models.PROTECT)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    income_range = models.CharField(max_length=20, choices=INCOME_RANGE_CHOICES)
    education_level = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(
        max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True, null=True
    )
    homeowner_status = models.CharField(
        max_length=10, choices=HOMEOWNER_STATUS_CHOICES, blank=True, null=True
    )
    number_of_children = models.IntegerField()
    occupation = models.CharField(max_length=255)
    ethnicity = models.CharField(max_length=255)
    language_preference = models.CharField(max_length=50)
    data_source = models.CharField(max_length=255)
    data_retrieval_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Demographic data for {self.customer}"
