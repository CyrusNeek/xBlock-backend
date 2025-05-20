from django.db import models
from django.conf import settings

class MeetingFile(models.Model):

    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    meeting = models.ForeignKey('Meeting', on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  
    type = models.CharField(max_length=20,null=True, blank=True)
    path = models.CharField(max_length=1024,null=True, blank=True)
    file = models.ForeignKey('Fileblock', on_delete=models.CASCADE,null=True, blank=True)
    
    # file_id = models.CharField(max_length=255,null=True,blank=True)


