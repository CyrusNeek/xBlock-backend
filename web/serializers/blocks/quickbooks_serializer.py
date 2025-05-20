
from web.models.quickbooks import QuickBooksCredentials
from rest_framework import serializers
from web.serializers import UnitSerializer

class QuickBooksCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickBooksCredentials
        fields = ['user', 'created_at', 'updated_at', "last_success_at", "name", "category", "unit", 'id']
        
    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        representation = super().to_representation(instance)
        representation['unit'] = UnitSerializer(instance.unit).data
        return representation