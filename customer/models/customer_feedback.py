from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomerFeedback(models.Model):
    PENDING = "Pending"
    RESPONDED = "Responded"

    RESPONSE_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (RESPONDED, "Responded"),
    ]

    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    feedback_date = models.DateField()
    feedback_time = models.TimeField()
    channel = models.CharField(max_length=255)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comments = models.TextField()
    response_status = models.CharField(
        max_length=10, choices=RESPONSE_STATUS_CHOICES, default=PENDING
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Feedback {self.pk} from Customer {self.customer}"
