from .user import User
from django.db import models
from .unit import Unit


class Group(models.Model):
    name = models.CharField(max_length=100)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
    permission_level = models.IntegerField(blank=True, default=0)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.unit.name + " - " + self.name
