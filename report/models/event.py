from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    location = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)