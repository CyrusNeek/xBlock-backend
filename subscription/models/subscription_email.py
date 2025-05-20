from django.db import models
from django.core.validators import MinValueValidator


class SubscriptionEmail(models.Model):
    AFTER = 'AFTER'
    BEFORE = 'BEFORE'
    SAME = 'SAME'
    
    TIME_CHOICES = [
        (AFTER, 'AFTER'),
        (BEFORE, 'BEFORE'),
        (SAME, 'SAME'),
    ]
    
    title = models.CharField(max_length=255, blank=True, null=True)
    
    send_time = models.CharField(max_length=10, choices=TIME_CHOICES, default=BEFORE)
    days = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    personal_email_template_id = models.CharField(max_length=100, blank=True, null=True)
    business_email_template_id = models.CharField(max_length=100, blank=True, null=True)
    send_clock = models.TimeField(null=True, blank=True, help_text="Time of day to send the email")
    sender_email = models.CharField(max_length=255,blank=True,null=True)


    
    

    class Meta:
        verbose_name = "email setting"
        verbose_name_plural = "email settings"