from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField(auto_now=True)
    end_time = models.TimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name