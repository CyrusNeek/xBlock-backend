from rest_framework import serializers, status
from rest_framework.response import Response
from web.models import Brand, Unit, UserBrand
from web.models.brand_owner import BrandOwner
from subscription.models import UserSubscription
from web.serializers.unit_serializer import UnitSerializer
from web.utils.push_notification import PushNotification


class SubBrandSerializer(serializers.ModelSerializer):
    units = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["id", "name", "units", "email", "description"]

    def get_units(self, obj):
        return UnitSerializer(obj.units.all(), many=True).data  



class SubBrandCreateSerializer(serializers.ModelSerializer):
    units = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()), write_only=True
    )
    units_response = serializers.SerializerMethodField()  # Add this field to return units

    class Meta:
        model = Brand
        fields = ["name", "email", "description", "units", "units_response"]

    def validate_units(self, units):
        for unit in units:
            if "address" not in unit or "website" not in unit:
                raise serializers.ValidationError(
                    "Each unit must contain 'address' and 'website'."
                )
        return units

    def create(self, validated_data):
        units_data = validated_data.pop("units", [])
        units_count = len(units_data)

        request = self.context.get("request")
        user = request.user

        try:
            brand_owner = BrandOwner.objects.get(pk=user.affiliation.pk)
        except BrandOwner.DoesNotExist:
            raise serializers.ValidationError("No primary brand found for the user.")

        try:
            user_plan = UserSubscription.objects.filter(
                brand_owner=brand_owner, status=UserSubscription.ACTIVE
            ).first()
        except UserSubscription.DoesNotExist:
            raise serializers.ValidationError(
                "No active subscription found for the brand owner."
            )

        primary_brand = Brand.objects.filter(owner=brand_owner, affiliation__isnull=True).first()
        sub_brand_count = Brand.objects.filter(owner=brand_owner, affiliation__isnull=False).count()  # Get existing sub-brands count
        # Check subscription limits
        if user_plan.max_sub_brand > sub_brand_count:
            if user_plan.max_unit_per_brand > units_count:
                sub_brand = Brand.objects.create(owner=brand_owner,affiliation=primary_brand, **validated_data)
                user_brand = UserBrand.objects.create(user=user, brand=sub_brand)  # Save user-brand relation
                
                created_units = []  # Store created units for response
                for unit_data in units_data:
                    try:
                        unit = Unit.objects.create(
                            address=unit_data["address"],
                            website=unit_data["website"],
                            name=unit_data["name"],
                            brand=sub_brand,
                            email=sub_brand.email,
                        )
                        created_units.append(unit)
                        user.units.add(unit) 

                    except Exception as e:
                        raise serializers.ValidationError(f"Error creating unit: {str(e)}")
                
                # Attach created units to the instance for response
                sub_brand.created_units = created_units  
                return sub_brand
            else:
                raise serializers.ValidationError(
                    "Failed to create sub brand locations, User subscription plan reached maximum location numbers per sub-brand."
                )
        else:
            raise serializers.ValidationError(
                f"You've reached your sub-brand limit. Your current plan allows a maximum of {user_plan.max_sub_brand} sub-brands. Upgrade to a higher plan to add more."
            )

    def get_units_response(self, obj):
        """Return units associated with the sub-brand"""
        if hasattr(obj, 'created_units'):
            return [
                unit.id
                for unit in obj.created_units
            ]
        return [unit.id
                for unit in Unit.objects.filter(brand=obj)]


class SubBrandObjectUnitSerializer(serializers.ModelSerializer):
    location_address = serializers.CharField(source="name")
    location_url = serializers.CharField(source="website")

    class Meta:
        model = Unit
        fields = ["id", "address", "website","name"]


class SubBrandObjectSerializer(serializers.ModelSerializer):
    units = SubBrandObjectUnitSerializer(many=True)

    class Meta:
        model = Brand
        fields = [
            "id",
            "brand_image_url",
            "name",
            "email",
            "description",
            "units",
        ]


class SubBrandObjectUpdateSerializer(serializers.ModelSerializer):
    units = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Brand
        fields = [
            "name",
            "email",
            "description",
            "units",
        ]

    # def update(self, instance, validated_data):
    #     units_data = validated_data.pop("units", [])
    #     units_count = len(units_data)
    #     request = self.context.get("request")
    #     user = request.user

    #     try:
    #         user_plan = UserSubscription.objects.get(
    #             brand_owner=instance.owner, status=UserSubscription.ACTIVE
    #         )
    #     except UserSubscription.DoesNotExist:
    #         raise serializers.ValidationError("User subscription not found.")

    #     existing_units = instance.units.all()
    #     existing_units_dict = {unit.name: unit for unit in existing_units}
    #     new_units_dict = {unit["location_address"]: unit for unit in units_data}

    #     if user_plan.max_unit_per_brand >= units_count:
    #         # Handle units update and deletion
    #         for unit_name, unit_obj in existing_units_dict.items():
    #             if unit_name in new_units_dict:
    #                 unit_data = new_units_dict[unit_name]
    #                 unit_obj.website = unit_data.get("location_url", unit_obj.website)
    #                 unit_obj.save()
    #             else:
    #                 unit_obj.delete()

    #         # Handle new units creation
    #         for unit_name, unit_data in new_units_dict.items():
    #             if unit_name not in existing_units_dict:
    #                 if "location_url" in unit_data:
    #                     Unit.objects.create(
    #                         name=unit_name,
    #                         website=unit_data["location_url"],
    #                         brand=instance,
    #                         address=instance.owner.address,
    #                         email=instance.email,
    #                     )
    #                 else:
    #                     raise serializers.ValidationError(
    #                         "Location URL is required for new units."
    #                     )
    #     else:
    #         notif = PushNotification()
    #         notif.send_notification(
    #             user=user,
    #             title="Failed to add Locations for this sub brand",
    #             body=f"You are trying to add {units_count} locations, which exceeds the maximum of {user_plan.max_unit_per_brand} locations allowed per sub-brand by your current subscription plan. To add more locations, please upgrade your plan or remove unnecessary locations.",
    #         )
    #         raise serializers.ValidationError(
    #             "Failed to update sub brand locations, User subscription plan reached maximum location numbers per sub-brand"
    #         )

    #     # Update the other fields of the sub-brand instance
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()

    #     return instance

    def update(self, instance, validated_data):
        units_data = validated_data.pop("units", None)  # None means key not provided
        existing_units = {unit.id: unit for unit in instance.units.all()}  # Use related_name="units"

        if units_data is not None:
            # Get unit IDs from the request
            new_unit_ids = {unit.get("id") for unit in units_data if "id" in unit}

            # Delete units that are not in the request
            for unit_id, unit in existing_units.items():
                if unit_id not in new_unit_ids:
                    unit.delete()

            # Update or create new units
            for unit_data in units_data:
                unit_id = unit_data.get("id")
                if unit_id and unit_id in existing_units:
                    # Update existing unit
                    unit = existing_units[unit_id]
                    for attr, value in unit_data.items():
                        setattr(unit, attr, value)
                    unit.save()
                else:
                    # Create new unit if id not provided
                    Unit.objects.create(brand=instance, **unit_data)

        # Update brand fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    





