from rest_framework import serializers
from report.models import Event


class ReportEventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = ['created_at', 'date', 'link', 'name']

