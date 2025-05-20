from django.db import models
from web.models import Unit

class BlockBase(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        "BlockCategory",
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
    )
    description = models.TextField(null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name + " - " + self.unit.name if self.unit else ""
