
from report.models import Event

from rest_framework import serializers



class EventSerializer(serializers.ModelSerializer):
  class Meta:
    fields = ['name', 'link', 'date', 'created_at', 'id', 'location']
    model = Event



