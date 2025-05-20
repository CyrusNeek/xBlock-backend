from django.db import models


class ShiftDetail(models.Model):
    staff = models.ForeignKey("pos.Staff", on_delete=models.CASCADE)
    restaurant = models.ForeignKey("pos.RestaurantLocation", on_delete=models.CASCADE)
    shift_date = models.DateField()
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    role = models.CharField(max_length=100)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    tips_earned = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shift {self.pk}"
