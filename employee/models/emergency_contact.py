from django.db import models


class EmergencyContact(models.Model):
    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contact_name} ({self.relationship})"
