from rest_framework import viewsets, status
from rest_framework.response import Response
from web.models import UnitFile
from web.serializers import UnitFileSerializer
from django.conf import settings
from web.services.storage_service import StorageService


S3_FOLDER_NAME = settings.S3_UNIT_FILE_FOLDER


class UnitFileViewSet(viewsets.ModelViewSet):
    queryset = UnitFile.objects.all()
    serializer_class = UnitFileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_presigned_post_url(self, unit, file_name):
        file_path = f"{S3_FOLDER_NAME}/{unit}/{file_name}"
        presigned_url, data = StorageService().generate_presigned_upload_url(file_path)

        return presigned_url, data, file_path

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data.get("unit")
        file_name = serializer.validated_data.get("file_name")
        file_size = serializer.validated_data.get("file_size")
        file_type = serializer.validated_data.get("file_type")
        category = serializer.validated_data.get("category")

        # Get presigned post URL
        presigned_url, presigned_post_data, path = self.get_presigned_post_url(
            unit, file_name
        )

        # Create the UnitFile instance with presigned URL
        file_description = request.data.get("file_description", "")
        unit_file = UnitFile.objects.create(
            user=request.user,
            file_url=path,
            file_description=file_description,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            category=category
        )

        # Prepare the response data
        response_data = serializer.data
        response_data["presigned_post_data"] = presigned_post_data
        response_data["id"] = unit_file.id
        response_data["file_url"] = presigned_url
        return Response(response_data, status=status.HTTP_201_CREATED)
