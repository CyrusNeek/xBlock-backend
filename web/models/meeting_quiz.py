from django.db import models
from web.models import Meeting, User


class MeetingQuiz(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    choices = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.meeting} - {self.text}"
    
    