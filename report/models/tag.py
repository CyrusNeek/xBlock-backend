from django.db import models
from web.models import Unit


class Tag(models.Model):
    name = models.CharField(max_length=300, unique=True)
    user = models.ForeignKey(
        "TockAuth", on_delete=models.CASCADE, null=True, blank=True
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    # class Meta:
    #     unique_together = ["user", "name"]
