from rest_framework import serializers
from ...models import URLBlock
from web.serializers import UnitSerializer


class URLBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLBlock
        fields = "__all__"
        
    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        representation = super().to_representation(instance)
        representation['unit'] = UnitSerializer(instance.unit).data
        return representation