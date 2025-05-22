from django.db import models


class StaffAssignment(models.Model):
    reservation = models.ForeignKey(
        "reservation.Reservation", on_delete=models.PROTECT, related_name="staff_assignment"
    )
    staff_member_id = models.CharField(max_length=255, null=True, blank=True)
    staff_member_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, null=True, blank=True)
    notes_for_staff = models.TextField(null=True, blank=True)
    turnover_time = models.IntegerField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assignment {self.pk} for Reservation {self.reservation}"
