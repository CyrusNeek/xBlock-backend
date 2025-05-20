from rest_framework import serializers
from report.models import TockAuth
from web.serializers import UnitSerializer
from report.tasks.periodic.tock_crawler import crawl_tock_periodic


class TockAuthSerializer(serializers.ModelSerializer):
    location_id = serializers.CharField(required=True)

    class Meta:
        model = TockAuth
        fields = [
            "id",
            "unit",
            "email",
            "password",
            "created_at",
            "updated_at",
            "status",
            "location_id",
            "block_category",
            "error_detail",
        ]

    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        representation = super().to_representation(instance)
        representation["unit"] = UnitSerializer(instance.unit).data
        return representation

    def save(self, **kwargs):
        saved = super().save(**kwargs, status=TockAuth.PENDING, error_detail=None)
        crawl_tock_periodic.delay(saved)
        return saved
