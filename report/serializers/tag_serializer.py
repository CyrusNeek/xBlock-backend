from rest_framework import serializers
from report.models import Tag


class TagSerializer(serializers.ModelSerializer):
  class Meta:
    fields = "__all__"
    model = Tag

