from django.db import models


class Department(models.Model):
    department_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    manager = models.ForeignKey(
        "employee.Manager",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    location = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.department_name
