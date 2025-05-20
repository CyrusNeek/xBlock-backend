from rest_framework import serializers
from report.models import ToastAuth
from web.serializers import UnitSerializer
from report.signals.toast_auth_signals import generate_ssh_key
from report.tasks.periodic.toast.order_details_crawl import crawl_toast_order_details

class ToastAuthSerializer(serializers.ModelSerializer):
    public_key = serializers.CharField(source='sshkey.public_key', read_only=True)

    class Meta:
        model = ToastAuth
        fields = ['id', 'unit', 'location_id', 'username', 'host', 'created_at', 'updated_at', 'public_key', 'status', 'block_category', 'error_detail']
        
        
    def create(self, validated_data):
        self.instance = ToastAuth(**validated_data)
        self.instance.save()
        self.instance.sshkey = generate_ssh_key(self.instance)
        self.instance.sshkey.save()
        
        return self.instance

    def to_representation(self, instance):
        """
        Modify the representation of the instance for read operations.
        """
        
        representation = super().to_representation(instance)
        representation['unit'] = UnitSerializer(instance.unit).data
        return representation
    
    
    def save(self, **kwargs):
        saved = super().save(**kwargs, status=ToastAuth.UNVERIFIED, error_detail=None)
        
        crawl_toast_order_details.delay(saved.pk, saved.is_initial_triggered)
        return saved