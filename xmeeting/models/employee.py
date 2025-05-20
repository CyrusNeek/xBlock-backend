from django.db import models


class Employee(models.Model):
    class Meta:
        db_table = 'meeting.xmeeting_employee'

        
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=150,null=True,blank=True)

    department = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    manager = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    upload_bucket = models.BooleanField(default=False)
    user_id = models.TextField(null=True, blank=True)
    unit_id = models.TextField(null=True, blank=True)
    

    username = models.CharField(max_length=150,null=True,blank=True)


    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_title} ()"

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
