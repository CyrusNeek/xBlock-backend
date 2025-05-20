from report.models import ResyReservation
from rest_framework import serializers


class ResyReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResyReservation
        fields = "__all__"
