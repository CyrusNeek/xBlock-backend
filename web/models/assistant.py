from django.db import models
from web.models.user import User
from web.models.openai_file import OpenAIFile


class Assistant(models.Model):
    PURPOSE_DEFAULT = "default"
    PURPOSE_BETTER_SERVE = "BetterServe"
    PURPOSE_CHOICES = [
        (PURPOSE_DEFAULT, "Default"),
        (PURPOSE_BETTER_SERVE, "Better Serve"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assistant_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model_type = models.CharField(max_length=255)
    vector_store_id = models.CharField(max_length=255, null=True)
    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
        default=PURPOSE_DEFAULT,
    )
    files = models.ManyToManyField(OpenAIFile, blank=True)

    def __str__(self):
        return f"{self.user} OpenAI Assistant {self.purpose}"
