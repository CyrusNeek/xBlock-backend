from django.db import models
from django.conf import settings

class Chat(models.Model):
    class Meta:
        db_table = 'history"."chat'

    ROLE_CHOICES = [
        ("user", "user"),
        ("assistant", "assistant"),
    ]

    thread = models.ForeignKey('Thread', related_name='chats', on_delete=models.CASCADE)
    user = models.ForeignKey("User", related_name='user_chats', on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chat_type = models.CharField(max_length=100)
    role = models.CharField(
        max_length=15, choices=ROLE_CHOICES
    )
    media_content = models.TextField()
    media_url = models.CharField(max_length=200)
    media_type = models.CharField(max_length=50)



    
    