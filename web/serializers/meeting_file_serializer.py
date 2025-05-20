from rest_framework import serializers
from web.models import MeetingFile
import mimetypes
from web.services.storage_service import StorageService
from web.services.id_service import generate_short_id
from vtk.services import upload_file_to_gcs
from report.tasks.periodic.openai_helper import upload_file_to_open_ai
import os

ALLOWED_MIME_TYPES = {
    "application/pdf",  # PDF
    "text/plain",  # TXT
    "application/msword",  # DOC
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "application/vnd.ms-excel",  # XLS
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX
    "text/csv",  # CSV
    "image/png",  # PNG
    "image/jpeg",  # JPG/JPEG
    "image/gif",  # GIF
}

class MeetingFileSerializer(serializers.ModelSerializer):
    # file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = MeetingFile
        fields = ['id', 'meeting', 'file', 'created_at' , 'name' , 'type' ]


    # def create(self, validated_data):
        # file = validated_data.pop("file")  

        # mime_type, _ = mimetypes.guess_type(file.name)

        # if mime_type not in ALLOWED_MIME_TYPES:
        #     raise serializers.ValidationError(f"Invalid file type: {mime_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}")

        # validated_data["type"] = mime_type
        # file_extension = os.path.splitext(file.name)[1].lower()
        # unique_name = generate_short_id()
        # file_name = f"meetings/{unique_name}{file_extension}".replace(" ", "_")
        # presigned_url , data = StorageService().generate_presigned_upload_url(file_name)
        # upload_file_to_gcs(presigned_url,data, file)

        # validated_data["path"] = file_name

        # return super().create(validated_data)
    


class MeetingFileGetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MeetingFile
        fields = ['id', 'meeting', 'url', 'created_at' , 'name' , 'type' ]

    def get_url(self, obj):
        if obj and obj.path:
            return StorageService().generate_presigned_download_url(obj.path)
        else:
            return None