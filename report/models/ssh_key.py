from django.db import models
from .toast_auth import ToastAuth


class SSHKey(models.Model):
    public_key = models.TextField()
    private_key_location = models.CharField(max_length=1024)

    created_at = models.DateTimeField(auto_now_add=True)
    toast_auth = models.OneToOneField(
        ToastAuth, on_delete=models.CASCADE, related_name="sshkey"
    )
