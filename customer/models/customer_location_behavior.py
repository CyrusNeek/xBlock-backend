from django.db import models


class CustomerLocationBehavior(models.Model):
    STORE = "store"
    COMPETITOR = "competitor"
    OTHER = "other"

    LOCATION_TYPE_CHOICES = [
        (STORE, "Store"),
        (COMPETITOR, "Competitor"),
        (OTHER, "Other"),
    ]

    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    location = models.CharField(max_length=255)
    visit_date = models.DateField()
    visit_time = models.TimeField()
    visit_duration_minutes = models.IntegerField()
    visit_frequency = models.IntegerField()
    location_type = models.CharField(
        max_length=50, choices=LOCATION_TYPE_CHOICES, default=STORE
    )
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    data_source = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"VisitRecord {self.pk} for {self.customer}"
