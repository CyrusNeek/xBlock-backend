from django.db import models
from django.conf import settings
from django.utils.timezone import now

class UserDailyUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=now)
    tokens_used = models.PositiveIntegerField(default=0)
    meetings_duration = models.PositiveIntegerField(default=0)
    stk_duration = models.PositiveIntegerField(default=0)
    upload_size = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")
