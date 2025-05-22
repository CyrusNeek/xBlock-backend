from rest_framework import serializers

from web.models.export_model import ExportModel
from web.serializers.document_serializer import DocumentSerializer

class ExportModelSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExportModel
        fields = ['id' , 'title','description' , 'children','documents'] 

    def get_children(self, obj):
        children = obj.children.filter(is_enabled=True)  
        return ExportModelSerializer(children, many=True, context=self.context).data