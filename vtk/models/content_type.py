from django.db import models
import uuid


class ContentType(models.Model):
    class Meta:
        db_table = 'speech_to_knowledge"."content_type'

    SUMMARY = "summary"
    QUIZ = "quiz"
    SOP = "SOP"

    CONTENT_TYPE_CHOICES = [(SUMMARY, "Summary"), (QUIZ, "Quiz"), (SOP, "SOP")]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    description = models.TextField()
    notes = models.TextField(blank=True, null=True)
    upload_bucket = models.BooleanField(default=False)

    class Meta:
        managed = True

    def __str__(self):
        return self.content_type

    def save(self, *args, **kwargs):
        self.upload_bucket = False
        super().save(*args, **kwargs)
