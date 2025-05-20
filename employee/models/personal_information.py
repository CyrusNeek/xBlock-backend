from django.db import models


class PersonalInformation(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    employee = models.ForeignKey("Employee", on_delete=models.CASCADE)
    birthdate = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
    )
    marital_status = models.CharField(max_length=50)
    nationality = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    personal_email = models.EmailField()
    personal_phone = models.CharField(max_length=15)
    upload_bucket = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        
        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Personal Information for {self.employee}"
