from django.db import models
from web.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(null=True)
    title = models.CharField(max_length=255, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
            ordering = ['-created_at']
            
    def __str__(self):
        return self.user.name + " - " + self.message
    
    def mark_as_read(self):
        self.read = True
        self.save()