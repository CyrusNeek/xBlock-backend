from web.models.document import Document
from rest_framework.response import Response
from rest_framework import status

from web.models.user import User
from web.serializers.document_serializer import DocumentSerializer


def update_document_speaker(document_id : int , user : User , speaker_name : str ) -> bool :
    filter_params = {
            'created_by': user,
            'id': document_id
        }

    try:
        document = Document.objects.get(**filter_params)
    except Document.DoesNotExist:
        return Response({"detail": "Document not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
    
    diarization_text = document.diarization_text or ""  
    updated_text = diarization_text.replace(speaker_name, user.full_name)

    data = {'diarization_text': updated_text }

    serializer = DocumentSerializer(document, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)