from django.db import models
from django.contrib.postgres.fields import ArrayField


class KnowledgeBaseContribution(models.Model):

    ARTICLE = "article"
    VIDEO = "video"
    PRESENTATION = "presentation"
    TALK = "talk"

    CONTENT_CHOICES = [
        (ARTICLE, "Article"),
        (VIDEO, "Video"),
        (PRESENTATION, "Presentation"),
        (TALK, "Talk"),
    ]

    employee = models.ForeignKey("employee.Employee", on_delete=models.CASCADE)
    contribution_date = models.DateField()
    content_type = models.CharField(max_length=15, choices=CONTENT_CHOICES)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    content_uri = models.TextField(null=True, blank=True)
    keywords = ArrayField(
        models.CharField(max_length=50), blank=True, null=True, default=list
    )
    views_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    likes_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    comments_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    upload_bucket = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):

        self.upload_bucket = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Contribution by {self.employee} - {self.title}"
