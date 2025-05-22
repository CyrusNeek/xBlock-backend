from rest_framework import serializers
from .models import Unit

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'symbol', 'created_at', 'updated_at'] 