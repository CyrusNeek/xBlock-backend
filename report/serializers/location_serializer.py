from rest_framework import serializers
from report.models import ReportLocation
from web.models import Unit


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Unit
