from django.db import models


class Manager(models.Model):
    manager_level = models.IntegerField(null=True, blank=True)
    employee = models.ForeignKey(
        "employee.Employee",
        on_delete=models.DO_NOTHING,
        related_name="manager_info",
        null=True,
        blank=True,
    )
    reports_to = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="reports_from",
        blank=True,
    )
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Manager {self.pk} (Level: {self.manager_level})"
