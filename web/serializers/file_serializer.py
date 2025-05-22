from rest_framework import serializers
from web.models import UnitFile


class UnitFileSerializer(serializers.ModelSerializer):
    file_url = serializers.URLField(max_length=1024, required=False, write_only=True)
    presigned_get_url = serializers.URLField(read_only=True)

    class Meta:
        model = UnitFile
        fields = "__all__"
