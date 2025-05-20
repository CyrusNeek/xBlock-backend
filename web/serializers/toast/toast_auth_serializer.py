from rest_framework import serializers
from report.models import ToastAuth
from web.serializers import UnitSerializer

class ToastAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = ToastAuth
        fields = ['id', 'unit', 'created_at', 'updated_at', 'status', 'block_category']

    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        representation = super().to_representation(instance)
        representation['unit'] = UnitSerializer(instance.unit).data
        return representation
