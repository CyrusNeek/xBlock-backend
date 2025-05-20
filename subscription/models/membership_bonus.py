from django.db import models
from django.core.validators import MinValueValidator

class MembershipBonus(models.Model):
    token = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    minute = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.objects.all().delete()
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name_plural = "membership bonuses"
