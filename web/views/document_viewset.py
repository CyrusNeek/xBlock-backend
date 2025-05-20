from faulthandler import is_enabled
from django.conf import settings
from rest_framework import viewsets
from report.tasks.periodic.openai_helper import upload_pdf_to_open_ai
from report.tasks.periodic.update_assistant_vector_files import update_assistant_vector_files
from vtk.models.xclassmate import XClassmate
from web.models import ExportModel, block_category
from web.models import document
from web.models.assistant import Assistant
from web.models.document import Document
from web.models.meeting import Meeting
from web.models.openai_file import OpenAIFile
from web.serializers import ExportModelSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from web.serializers.document_serializer import DocumentSerializer
from web.serializers.meeting_serializer import MeetingSerializer
from web.services import Whisper
from openai import OpenAI
from web.services.openai_service import OpenAIService
from web.services.file_service import FileService
import time 
import datetime

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class DocumentViewSet(APIView):
    permission_classes = [IsAuthenticated]

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get(self, request, recording_id=None, *args, **kwargs):
        filter_params = {
            'is_enabled': True,
            'created_by': request.user
        }

        doc_type = request.query_params.get('type', None)
        if doc_type:
            filter_params['type'] = doc_type
        else:
            filter_params['type'] = "vtk"  

        if recording_id:
            if doc_type == "meeting":
                filter_params['meeting_id'] = recording_id
            elif doc_type == "vtk":
                filter_params['classmate_id'] = recording_id

        documents = Document.objects.filter(**filter_params)
        print("Filtered Documents:", documents)
        print("Filter Params:", filter_params)

        export_models = ExportModel.objects.filter(
            type=doc_type if doc_type else "vtk",  
            is_enabled=True
        )
        print("Filtered Export Models:", export_models)

        res = {}
        export_model_parent = export_models.filter(parent=None)
        print("Export Models with parent=None:", export_model_parent)

        for export_model in export_model_parent:
            print("Processing Export Model ID:", export_model.id)
            res[export_model.id] = {
                "title": export_model.title,
                "description": export_model.description,
                "children": []
            }

            for child in export_model.children.all():
                child_documents = child.documents.filter(**filter_params)
                print("Child ID:", child.id, "Filtered Documents Query for Export Model ID:", export_model.id)
                print(child_documents.query)
                res[export_model.id]["children"].extend(DocumentSerializer(child_documents, many=True).data)

        return Response(res, status=status.HTTP_200_OK)


    def delete(self, request, recording_id=None, *args, **kwargs):
        filter_params = {
            'created_by': request.user,
            'id': recording_id
        }
        try:
            document = Document.objects.get(**filter_params)
            document.delete()
            return Response(
                {"message": "Document deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, recording_id, export_model_id, recording_type,   *args, **kwargs):
        data=request.data

        serializer = self.serializer_class(
            data=request.data, context={'request': request})

        if recording_type == "meeting":
            recording = self.find_meeting(recording_id)
        else:
            recording = self.find_classmate(recording_id)

        export_model = self.find_export_model(export_model_id)

        if not recording:
            return Response({"error": "recording not found."}, status=status.HTTP_404_NOT_FOUND)
        if not export_model:
            return Response({"error": "Export model not found."}, status=status.HTTP_404_NOT_FOUND)

        is_classmate = False
        if recording_type == "vtk":
            is_classmate = True
        diarization_text = Whisper().retrieve_user_voice_text(
            request.user.id, recording.id, is_classmate)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{export_model.prompt , export_model.instructions , export_model.output_format }"},
                {"role": "user", "content": f"{diarization_text}"},
            ],
            temperature=0,
        )
        res = str(completion.choices[0].message.content)
        now = datetime.datetime.now()

        pdf_content = "document type: document - " 
        pdf_content += "document title: " + data["block_name"] + " "
        pdf_content += "document description: " + data["block_description"] + " "
        pdf_content += "document creation time: " + str(now) + " " + res

        pdf = FileService.create_pdf_from_text(pdf_content)
        file = OpenAIService.upload_file(pdf)
        if serializer.is_valid():
            if recording_type == "meeting":
                serializer.save(created_by=request.user, meeting=recording, export_model=export_model,
                                diarization_text=diarization_text, content=res, type="meeting", file_id=file.id)
            else:
                serializer.save(created_by=request.user, classmate=recording, export_model=export_model,
                                diarization_text=diarization_text, content=res, type="vtk", file_id=file.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def find_meeting(self, id):
        try:
            return Meeting.objects.get(id=id)
        except Meeting.DoesNotExist:
            return None

    def find_classmate(self, id):
        try:
            return XClassmate.objects.get(id=id)
        except XClassmate.DoesNotExist:
            return None

    def find_export_model(self, id):
        try:
            return ExportModel.objects.get(id=id)
        except ExportModel.DoesNotExist:
            return None


class DocumentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, document_id=None, *args, **kwargs):
        filter_params = {
            'created_by': request.user,
            'id': document_id
        }

        try:
            document = Document.objects.get(**filter_params)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentSerializer(document, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            if(document.file_id):
                OpenAIService.delete_file(document.file_id)
            pdf_content = "document type: document - " 
            pdf_content += "document title: " + document.block_name + " "
            pdf_content += "document description: " + document.block_description + " "
            pdf_content += "document creation time: " + str(document.created_at) + " " + document.content
            pdf = FileService.create_pdf_from_text(pdf_content)
            file = OpenAIService.upload_file(pdf)
            document.file_id = file.id
            document.save(update_fields=["file_id"]) 
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentXbrain(APIView):
    def patch(self, request, document_id=None, *args, **kwargs):
        user = request.user
        filter_params = {
            # 'created_by': request.user,
            'id': document_id
        }

        try:
            document = Document.objects.get(**filter_params)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        
        data = {'is_added_xbrain': request.data.get('is_added_xbrain')}
        serializer = DocumentSerializer(document, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()

        user_assistant = Assistant.objects.filter(
            user=user
            ).first()
        
        if document.is_added_xbrain:
            file = upload_pdf_to_open_ai(document.diarization_text) 
            print(file)
        
            openai_file = OpenAIFile.objects.create(
                file_name=file.filename,
                file_id=file.id,
                block_category=document.block_category,  
                unit=document.unit,
                model_name="unit-file"
            )

            user_assistant.files.add(openai_file)
            user_assistant.save()
            client.beta.vector_stores.file_batches.create(
                vector_store_id=user_assistant.vector_store_id,
                file_ids=[file.id]
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentTranslate(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def post(self, request, doc_id,   *args, **kwargs):
        try:
            document = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        lang = request.data.get('lang', '')
        if lang == '':
            return Response({"error": "Language not found."}, status=status.HTTP_404_NOT_FOUND)

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a professional translator with expertise in ensuring precise and accurate translations.\nTask:\n- Translate the following text into {lang}.\n- Maintain the original meanings, words, and sentence structures.\n- Ensure the translation is clear, contextually appropriate, and professional. \nInstructions:\n- Do not alter the meanings of the original text.\n- Keep the sentences and words as close to the original as possible.\n- Preserve the nuance and tone of the source text.\n- Use formal language if the original is formal, and informal language if the original is informal.\n\nTarget Language:\n- {lang} \nSource Text:\n- [{document.content}]"},],
            temperature=0,
        )
        res = str(completion.choices[0].message.content)
        print(res)
        new_doc = Document.objects.create(
            created_by=request.user,
            meeting=document.meeting,
            classmate=document.classmate,
            export_model=document.export_model,
            diarization_text=document.diarization_text,
            content=res,
            is_enabled=document.is_enabled,
            is_added_xbrain=document.is_added_xbrain,
            is_added_report=document.is_added_report,
            unit=document.unit,
            block_category=document.block_category,
            type=document.type,
            block_name=f"{document.block_name} - copy",
            block_description=document.block_description
        )

        pdf_content = "document type: translation file - " 
        pdf_content += "document title: " + document.block_name + " "
        pdf_content += "document description: " + document.block_description + " "
        pdf_content += "document creation time: " + str(document.created_at) + " " + document.content
        pdf = FileService.create_pdf_from_text(pdf_content)
        file = OpenAIService.upload_file(pdf)
        document.file_id = file.id
        document.save(update_fields=["file_id"]) 
        return Response({"message": "Document translated successfully", "data": DocumentSerializer(new_doc).data}, status=status.HTTP_200_OK)

