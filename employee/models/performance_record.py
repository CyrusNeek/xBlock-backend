from django.db import models


class PerformanceRecord(models.Model):
    PERFORMANCE_CHOICES = [
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("needs_improvement", "Needs Improvement"),
    ]

    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE)
    evaluation_date = models.DateField()
    evaluator_id = models.CharField(max_length=100)
    performance_score = models.FloatField()
    performance_rating = models.CharField(max_length=20, choices=PERFORMANCE_CHOICES)
    goals = models.CharField(max_length=255)
    feedback = models.CharField(max_length=255)
    employee_comments = models.TextField(blank=True, null=True)
    action_items = models.CharField(max_length=255)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Performance Record for {self.employee} on {self.evaluation_date}"
