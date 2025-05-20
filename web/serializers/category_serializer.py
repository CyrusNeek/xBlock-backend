from rest_framework import serializers

from web.models.category import Category

class CategoryFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 
            'title', 
            'description', 
            'is_enabled', 
            'priority', 
            'type'
        ]

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 
            'title', 
            'description', 
            'parent', 
            'is_enabled', 
            'priority', 
            'type', 
            'children',  
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_enabled=True)  
        return CategorySerializer(children, many=True, context=self.context).data

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
