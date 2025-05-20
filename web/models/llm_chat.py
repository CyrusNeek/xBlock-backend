from django.db import models
from django.utils import timezone
from .user import User

CHAT_MODELS = [
    ("GPT-3.5", "GPT-3.5-turbo-1106"),
    ("GPT-4", "GPT-4-1106-preview"),
]


class LLMChat(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="llm_chat"
    )
    messages = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model = models.CharField(
        max_length=20, choices=CHAT_MODELS, default="GPT-3.5", blank=True
    )
    thread_id = models.CharField(max_length=50, blank=True)
    new_models = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.new_models:  
            self.new_models = False
        super().save(*args, **kwargs)
    title = models.CharField(max_length=200,default="")

    def __str__(self):
        if not self.user:
            return f"Anonymous user at {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        elif hasattr(self.user, "affiliation") and self.user.affiliation:
            return f"{self.user.affiliation} {self.user.name} at {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return f"User {self.user.name} at {self.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
