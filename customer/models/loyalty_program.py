from django.db import models


class LoyaltyProgram(models.Model):
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

    MEMBERSHIP_LEVEL_CHOICES = [
        (SILVER, "Silver"),
        (GOLD, "Gold"),
        (PLATINUM, "Platinum"),
    ]

    program_name = models.CharField(max_length=255)
    enrollment_date = models.DateField()
    loyalty_points = models.IntegerField()
    membership_level = models.CharField(max_length=50, choices=MEMBERSHIP_LEVEL_CHOICES)
    notes = models.CharField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loyalty Program {self.pk} for {self.customer}"
