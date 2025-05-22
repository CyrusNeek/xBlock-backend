from django.db import models
from django.conf import settings
import uuid
    

class Thread(models.Model):
    class Meta:
        db_table = 'history"."thread'

    id = models.UUIDField(
        primary_key=True,  
        default=uuid.uuid4,  
        editable=False  
    )

    title = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_threads', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_assistant_thread = models.BooleanField(default=False)
    openai_threadid = models.CharField(max_length=100)


    def __str__(self):
        return self.title


