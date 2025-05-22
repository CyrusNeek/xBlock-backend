from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from web.models.category import Category
from web.serializers.category_serializer import CategorySerializer


class SubCategoryView(APIView):
    def get(self, request, parent_id, *args, **kwargs):
        try:
            subcategories = Category.objects.filter(parent_id=parent_id, is_enabled=True)

            if not subcategories.exists():
                return Response({"detail": "No subcategories found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(subcategories, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            return Response({"detail": "Parent category not found."}, status=status.HTTP_404_NOT_FOUND)
