from django.db import models
from django.contrib.auth import get_user_model
from .xclassmate import XClassmate


class XClassmateQuiz(models.Model):
    x_classmate = models.ForeignKey(XClassmate, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    choices = models.JSONField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.x_classmate} - {self.text}"
