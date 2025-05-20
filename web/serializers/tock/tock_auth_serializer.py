from rest_framework import serializers
from web.models import TockAuth
from web.serializers import UnitSerializer

class TockAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = TockAuth
        fields = ['id', 'unit', 'email', 'password', 'created_at', 'updated_at', 'status']

    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        representation = super().to_representation(instance)
        representation['unit'] = UnitSerializer(instance.unit).data
        return representation
