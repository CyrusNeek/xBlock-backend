from django.db import models
from web.models import User

class FirebaseCloudMessaging(models.Model):
    """
    Model for saving Firebase Cloud Messaging tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username}"
