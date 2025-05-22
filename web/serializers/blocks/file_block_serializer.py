from rest_framework import serializers

from web.models.unit import Unit
from ...models import FileBlock
from ..file_serializer import UnitFileSerializer
from web.serializers import UnitSerializer


class FileBlockSerializer(serializers.ModelSerializer):
    files = UnitFileSerializer(many=True, read_only=True)
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), required=False)

    class Meta:
        model = FileBlock
        fields = "__all__"
        
    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        representation = super().to_representation(instance)
        representation['unit'] = UnitSerializer(instance.unit).data
        return representation
    
    def validate(self, data):
        units = self.initial_data.get("units", [])
        if isinstance(units, list) and units:
            data['unit'] = units[0]  
        return data