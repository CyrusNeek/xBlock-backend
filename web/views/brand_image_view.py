from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from web.serializers import BrandImageSerializer
from web.models import Brand
from web.services.storage_service import StorageService
from vtk.services import upload_file_to_gcs

class BrandImageViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, brand_id, *args, **kwargs):
        brand = Brand.objects.get(id=brand_id)
        serializer = BrandImageSerializer(brand, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, brand_id, *args, **kwargs):
        brand = Brand.objects.get(id=brand_id)
        serializer = BrandImageSerializer(brand, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            filename = f"public/{brand.id}_{brand.name}.jpg".replace(
            " ", "_")
            brand.brand_image_url = filename
            presigned_url, data = StorageService().generate_presigned_upload_url(filename)
            uploaded_file = request.FILES.get("brand_image")

            uploaded = upload_file_to_gcs(presigned_url,data, uploaded_file)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, brand_id, *args, **kwargs):
        brand = Brand.objects.get(id=brand_id)
        brand.brand_image.delete(save=True)
        return Response({"detail": "Brand image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
