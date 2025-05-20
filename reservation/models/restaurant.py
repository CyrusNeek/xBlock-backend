from django.db import models


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=255)
    venue_address = models.TextField(blank=True, null=True)
    venue_capacity = models.IntegerField(blank=True, null=True)
    table_layout = models.TextField(null=True, blank=True)
    operational_notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.restaurant_name} - {self.pk}"
