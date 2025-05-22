from rest_framework import serializers
from report.models import SSHKey

class SSHKeySerializer(serializers.ModelSerializer):

    class Meta:
        model = SSHKey
        fields = ['id', 'public_key', 'toast_auth']