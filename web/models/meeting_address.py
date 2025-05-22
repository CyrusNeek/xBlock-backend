from django.db import models
from django.conf import settings

class MeetingAddress(models.Model):

    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    title = models.CharField(max_length=255,null=True, blank=True)
    address = models.CharField(max_length=255,null=True, blank=True)
    location = models.CharField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  


    


