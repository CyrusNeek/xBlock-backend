from django.db import models


class Reservation(models.Model):
    # RESERVATION_STATUS_CHOICES = [
    #     ("confirmed", "Confirmed"),
    #     ("canceled", "Canceled"),
    #     ("no-show", "No Show"),
    #     ("completed", "Completed"),
    # ]

    reservation_source = models.CharField(max_length=255)
    restaurant = models.ForeignKey(
        "Restaurant", on_delete=models.PROTECT, related_name="reservation"
    )
    reservation_date = models.CharField(null=True, blank=True, max_length=255)
    reservation_time = models.TimeField(blank=True, null=True)
    booking_datetime = models.DateTimeField(auto_now_add=True)
    reservation_status = models.CharField(max_length=20, blank=True, null=True)
    number_of_guests = models.PositiveIntegerField(blank=True, null=True)
    table_number = models.CharField(max_length=50, null=True, blank=True)
    special_requests = models.TextField(null=True, blank=True)
    reservation_channel = models.CharField(max_length=255, null=True, blank=True)
    cancellation_datetime = models.DateTimeField(null=True, blank=True)
    check_in_status = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    waitlist_position = models.IntegerField(null=True, blank=True)
    confirmation_method = models.CharField(max_length=255, null=True, blank=True)
    booking_notes = models.TextField(null=True, blank=True)
    guest = models.ForeignKey(
        "Guest", on_delete=models.PROTECT, related_name="reservation"
    )
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation for {self.restaurant.restaurant_name} : {self.pk}"


class ModificationHistory(models.Model):
    reservation = models.ForeignKey(
        Reservation, on_delete=models.PROTECT, related_name="modification_history"
    )
    modification = models.DateTimeField()
    modified_by = models.CharField(max_length=255)
    modification_notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Modification {self.modification} for Reservation {self.reservation.pk}"
