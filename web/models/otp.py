from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.expires_at > timezone.now()
    
    def __str__(self):
        if self.email:
            return self.email
        elif self.phone_number:
            return self.phone_number
        else:
            return "OTP object"

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTP"