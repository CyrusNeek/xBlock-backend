from rest_framework import serializers
from vtk.models.xclassmate import XClassmate
from web.models.block_category import BlockCategory
from web.models.document import Document
from web.models.export_model import ExportModel
from web.models.meeting import Meeting
from web.models.unit import Unit
from web.serializers.block_category_serializer import BlockCategorySerializer
from web.serializers.unit_serializer import UnitSerializer


class DocumentSerializer(serializers.ModelSerializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), required=False)  
    block_category = serializers.PrimaryKeyRelatedField(queryset=BlockCategory.objects.all(), required=False)  

    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.all(), required=False)
    classmate = serializers.PrimaryKeyRelatedField(queryset=XClassmate.objects.all(), required=False)
    # export_model = ExportModelSerializer(required=False)
    export_model = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'block_name', 'unit', 'block_category', 'block_description','created_at',
            'is_enabled', 'is_added_xbrain', 'is_added_report', 'diarization_text', 'content', 'meeting', 'classmate', 'content', 'export_model', 'type','file_id'
        ]
        extra_kwargs = {
            'file_id': {'required': False, 'allow_null': True}  
        }

    def get_export_model(self, obj):
        return obj.export_model.title if obj.export_model else "-"
