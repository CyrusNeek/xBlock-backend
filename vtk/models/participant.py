from django.db import models
from django.conf import settings

class Participant(models.Model):
    
    PARTICIPANT_ROLE = [
        ("Host", "Host"),
        ("Co-Host", "Co-Host"),
        ("Participant", "Participant"),
        ("Guest", "Guest")
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    xclassmate = models.ForeignKey('XClassmate', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  
    is_guest = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=PARTICIPANT_ROLE,null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)

