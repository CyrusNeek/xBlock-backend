from rest_framework import serializers

from report.models import TockBooking

from .tag_serializer import TagSerializer


class TockBookingSerializer(serializers.ModelSerializer):
  tags = TagSerializer(many=True)
  
  class Meta:
    fields = ['report_triggered_at', 'time', 'status', 'tags', 'postal_code', 'guest_notes', 'dietary_notes', 'visit_tags', 'guest_tags', 'id', 'birthday']

    model = TockBooking