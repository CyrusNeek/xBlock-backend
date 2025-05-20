
from django.db import models


class Team(models.Model):

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    units = models.ManyToManyField("web.Unit", blank=True, related_name="teams")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    team_manager = models.ForeignKey("web.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="leaders")


    created_at = models.DateTimeField(auto_now_add=True)