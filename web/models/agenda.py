from django.db import models
from django.conf import settings
from web.models import Meeting


class Agenda(models.Model):
    meeting = models.ForeignKey(Meeting, related_name="agenda_items", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    time_allotted = models.IntegerField() 
    user = models.ForeignKey("User", related_name='user_agendas', on_delete=models.SET_NULL, null=True)

    speaker_name = models.CharField(max_length=255)

    
    def __str__(self):
        return self.title