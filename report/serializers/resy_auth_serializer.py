from rest_framework import serializers
from report.models import ResyAuth
from web.serializers import UnitSerializer
from report.tasks.periodic.resy_crawler import get_valid_reservation_dates_and_fetch, get_valid_ratings_and_fetch


class ResyAuthSerializer(serializers.ModelSerializer):
    location_id = serializers.CharField(required=True)

    class Meta:
        model = ResyAuth
        fields = ['id', 'unit', 'email', 'password', 'created_at', 'updated_at', 'status', 'location_id', 'block_category', 'error_detail']

    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        representation = super().to_representation(instance)
        representation['unit'] = UnitSerializer(instance.unit).data
        return representation
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        get_valid_reservation_dates_and_fetch.delay(instance.pk)
        get_valid_ratings_and_fetch.delay(instance.pk)

        return instance
    
class GetResyAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResyAuth
        fields = ['id', 'unit', 'email', 'created_at', 'updated_at', 'status', 'location_id', 'block_category', 'error_detail']
        read_only_fields = ['id', 'unit', 'email', 'created_at', 'updated_at', 'status', 'location_id', 'block_category', 'error_detail']
