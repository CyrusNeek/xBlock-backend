from django.db import models
from django.contrib.postgres.fields import ArrayField


class EmploymentDetail(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ("full_time", "Full-Time"),
        ("part_time", "Part-Time"),
        ("contractor", "Contractor"),
    ]

    WORK_SCHEDULE_CHOICES = [("9_5_shift", "9-5 Shift"), ("flexible", "Flexible")]

    WEEKLY = "weekly"
    BI_WEEKLY = "bi-weekly" 
    MOUNTHLY = "monthly"

    SALARY_FREQUENCY_CHOICES = [
        (WEEKLY, "Weekly"),
        (BI_WEEKLY, "Bi-weekly"),
        (MOUNTHLY, "Monthly"),
    ]

    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE)
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        blank=True,
        null=True,
    )
    work_schedule = models.CharField(
        max_length=20,
        choices=WORK_SCHEDULE_CHOICES,
        blank=True,
        null=True,
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pay_frequency = models.CharField(
        max_length=10,
        choices=SALARY_FREQUENCY_CHOICES,
        blank=True,
        null=True,
    )
    benefits_enrolled = ArrayField(
        models.CharField(max_length=100), blank=True, null=True
    )
    last_promotion_date = models.DateField(blank=True, null=True)
    performance_score = models.FloatField(blank=True, null=True)
    bonus_eligibility = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Employment details for {self.employee}"
