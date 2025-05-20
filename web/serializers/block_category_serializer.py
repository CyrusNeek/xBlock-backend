from rest_framework import serializers

from roles.models import Role
from web.models.unit import Unit
from ..models import BlockCategory


class BlockCategorySerializer(serializers.ModelSerializer):
    block_count = serializers.IntegerField(read_only=True)
    
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    brand_id = serializers.IntegerField(source="unit.brand_id", read_only=True)
    brand_name = serializers.SerializerMethodField(read_only=True, default="Global", initial="Global")

    # block_category_ids = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     queryset=Role.objects.all(),
    #     source='roles'
    # )

    units = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Unit.objects.all(),
    )


    class Meta:
        model = BlockCategory
        fields = "__all__"

    def get_brand_name(self, obj: BlockCategory):
        units = obj.units.all()
        brands_name = []

        for unit in units:
            brands_name.append(
                unit.brand.name
            )

        return ", ".join(brands_name)


