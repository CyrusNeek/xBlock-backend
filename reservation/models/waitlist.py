from django.db import models


class Waitlist(models.Model):
    STATUS_CHOICES = [
        ("WAITING", "Waiting"),
        ("SEATED", "Seated"),
        ("LEFT", "Left"),
    ]

    guest = models.ForeignKey(
        "Guest", on_delete=models.PROTECT, related_name="waitlist"
    )
    restaurant = models.ForeignKey(
        "Restaurant", on_delete=models.PROTECT, related_name="waitlist"
    )
    position = models.IntegerField()
    added_datetime = models.DateTimeField(auto_now_add=True)
    estimated_wait_time = models.IntegerField()
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Waitlist {self.pk} for Guest {self.guest}"
