from django.db import models
from web.models import Unit

class Reservation(models.Model):
    first_name = models.CharField(max_length=30)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    party_size = models.IntegerField(blank=True, null=True)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    
    area = models.CharField(max_length=30, blank=True)
    tables = models.CharField(max_length=100, blank=True)
    server_name = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    experience = models.TextField(blank=True)

    class Meta:
        unique_together = ('email', 'phone_number', 'reservation_date', 'reservation_time', 'area', 'tables', 'unit')

    def __str__(self):
        return f"Reservation {self.unit.name} on {self.reservation_date} at {self.reservation_time} for {self.first_name} {self.last_name}"