from rest_framework import serializers

from roles.models import Role
from ..models import Team
from web.models import User, Unit


class TeamManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class TeamSerializer(serializers.ModelSerializer):
    units = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Unit.objects.all(),
    )

    unit_names = serializers.SerializerMethodField()
    # team_manager = TeamManagerSerializer(read_only=True)


    class Meta:
        model = Team
        fields = "__all__"

    
    def get_unit_names(self, obj: Team):
        return ", ".join(obj.units.values_list("name", flat=True))


class TeamGetSerializer(serializers.ModelSerializer):
    units = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Unit.objects.all(),
    )

    unit_names = serializers.SerializerMethodField()
    team_manager = TeamManagerSerializer(read_only=True)
    parent = TeamSerializer(read_only=True)


    class Meta:
        model = Team
        fields = "__all__"

    
    def get_unit_names(self, obj: Team):
        return ", ".join(obj.units.values_list("name", flat=True))
    



