from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from web.models.category import Category
from web.serializers.category_serializer import CategorySerializer
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

class CategoryViewSet(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, category_id=None, *args, **kwargs):
        # If 'category_id' is provided, retrieve the category by ID
        if category_id:
            try:
                category = Category.objects.get(id=category_id, is_enabled=True)
                serializer = CategorySerializer(category, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            except ObjectDoesNotExist:
                return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Otherwise, return a list of top-level categories with optional filtering by 'type'
        else:
            category_type = request.query_params.get('type', None)

            filter_params = {
                'is_enabled': True,
                'parent__isnull': True,
            }

            if category_type:
                filter_params['type'] = category_type

            categories = Category.objects.filter(**filter_params)
            serializer = CategorySerializer(categories, many=True, context={'request': request})
        
            return Response(serializer.data, status=status.HTTP_200_OK)


    # def patch(self, request, brand_id, *args, **kwargs):
    #     brand = Brand.objects.get(id=brand_id)
    #     serializer = BrandImageSerializer(brand, data=request.data, partial=True, context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, brand_id, *args, **kwargs):
    #     brand = Brand.objects.get(id=brand_id)
    #     brand.brand_image.delete(save=True)
    #     return Response({"detail": "Brand image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
