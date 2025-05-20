from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from roles.constants import (
    XCLASSMATE_ACCESS,
)
from roles.models import Role
from vtk.models import XClassmate, XClassmateQuiz, Participant
from web.models.category import Category
from web.services.document_service import update_document_speaker
from web.services.storage_service import StorageService
from web.services.whisper import Whisper
from web.models import User
from vtk.serializers import (
    XClassmateSerializer,
    XClassmateQuizSerializer,
    XClassmateListSerializer,
    UpdateDiarizationRequestSerializer,
)
from django.conf import settings
from django.db.models import Q, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from roles.permissions import UserPermission
import logging
from drf_spectacular.utils import extend_schema
from web.pagination import StandardResultsSetPagination
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import filters

from vtk.signals import signal_trigger_xclassmate_summarize
from vtk.services import upload_file_to_gcs
from vtk.models import Participant
from web.services.openai_service import OpenAIService
from web.services.file_service import FileService

logger = logging.getLogger(__name__)


class XClassmateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = XClassmateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       OrderingFilter, filters.SearchFilter]

    def get_serializer_class(self): 
        if self.action == "list":
            return XClassmateListSerializer
        else:
            return XClassmateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            XClassmate.objects.select_related(
                "unit", "created_by", "category", "sub_category")
            .prefetch_related("participants")
            .annotate(task_count=Count("tasks"))
            .order_by("-created_at")
            .filter(created_by=user)
        )

        return queryset.filter(Q(participants=user) | Q(created_by=user))

    def get_presigned_post_url(self, user, xclassmate_id, file_name):
        presigned_post = StorageService().generate_presigned_upload_url(file_name)
        logger.info(presigned_post)
        return presigned_post

    def check_permission(self):
        return UserPermission.check_user_permission(
            self.request.user, XCLASSMATE_ACCESS
        )

    def perform_permissions_check(self, request):
        if not self.check_permission():
            raise PermissionDenied(
                "You don't have permission to perform this action."
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = XClassmateListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = XClassmateListSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_category(self, category_id):
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                return category
            except Category.DoesNotExist:
                return Response({"error": f"Category with id {category_id} not found"}, status=status.HTTP_400_BAD_REQUEST)

    # Modified create method
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        xclassmate_data = serializer.validated_data
        xclassmate_data["purpose"] = request.data.get("purpose", "")
        xclassmate_data["unit"] = user.unit or user.units.first()
        xclassmate_data["is_added_xbrain"] = True if request.data.get(
            "is_added_xbrain", False) == "true" else False
        xclassmate_data["is_added_report"] = True if request.data.get(
            "is_added_report", False) == "true" else False
        xclassmate_data["category"] = self.get_category(
            request.data.get("category"))
        xclassmate_data["sub_category"] = self.get_category(
            request.data.get("sub_category"))
        uploaded_file = request.FILES.get("file")
        
        xclassmate = serializer.save()

        xclassmate.filename = f"x_classmate/{user.first_name}_{xclassmate.id}.wav".replace(
            " ", "_")

        presigned_url, data = self.get_presigned_post_url(
            user, xclassmate.id, xclassmate.filename)
        xclassmate.recording_file_url = presigned_url

        uploaded = upload_file_to_gcs(presigned_url,data, uploaded_file)
        if not uploaded:
            return Response(
                {"error": f"failed to upload file"},
                status=400  
            )

        xclassmate.uploaded = True 
        xclassmate.save()

        signal_trigger_xclassmate_summarize(XClassmate, xclassmate, True)

        xclassmate_data = serializer.data
        xclassmate_data["presigned_post_data"] = data

        return Response(xclassmate_data)

    def get_presigned_get_url(self, file_name):
        presigned_url = StorageService().generate_presigned_download_url(file_name)
        return presigned_url

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Serialize xclassmate data
        xclassmate_data = XClassmateSerializer(instance).data

        # Generate a pre-signed URL for the WAV file if available
        if instance.filename:
            presigned_url = self.get_presigned_get_url(instance.filename)
            xclassmate_data["presigned_url"] = presigned_url

        return Response(xclassmate_data)


class WhisperDataView(APIView):

    # def check_permission(self):
    #     return UserPermission.check_user_permission(
    #         self.request.user, XCLASSMATE_ACCESS
    #     )

    def get(self, request, xclassmate_id, *args, **kwargs):
        page_size = request.GET.get("page_size", 10)
        page = request.GET.get("page", 1)

        whisper = Whisper()
        response = whisper.retrieve_user_voice(
            user_id=request.user.id,
            meeting_id=xclassmate_id,
            page_size=int(page_size),
            page_number=int(page),
            is_xclassmate=True,
        )
        return Response(response)

    @extend_schema(request=UpdateDiarizationRequestSerializer, tags=["xclassmates"])
    def put(self, request, xclassmate_id, *args, **kwargs):
        # Retrieve the xclassmate created by the user with the given primary key
        queryset = XClassmate.objects.filter(
            created_by=request.user, id=xclassmate_id
        ).first()

        # Check and update the speakers in the diarization field
        serializer = UpdateDiarizationRequestSerializer(data=request.data)
        
        if request.data.get("user_id"):
            new_user = (
                User.objects.select_related("unit", "role")
                .prefetch_related(
                    "units",
                    Prefetch(
                        "role",
                        queryset=Role.objects.prefetch_related(
                            "permissions", "block_category"
                        ),
                    ),
                )
                .filter(id=request.data.get("user_id"))
                .first()
            )
            full_name = new_user.full_name
            participant = Participant.objects.filter(xclassmate_id=xclassmate_id, user_id=request.data.get("user_id")).first()
            if not participant:
                participant = Participant()
                participant.user = new_user
                participant.full_name = new_user.full_name
                participant.is_guest = False
                participant.xclassmate = queryset
                participant.save()
        else:
            if "new_speaker" in request.data and request.data["new_speaker"] != "":
                full_name = request.data["new_speaker"]
            else:
                full_name = request.data["speaker"]

        if queryset and serializer.is_valid(raise_exception=True):
            serializer.validated_data["user_name"] = f"{full_name}"
            whisper = Whisper()
            response = whisper.update_speaker_name(
                user_id=queryset.created_by.id,
                meeting_id=queryset.id,
                payload=dict(serializer.validated_data),
                is_xclassmate=True,
            )
            #==== update pdf after renaming speaker ====
            full_content = queryset.name + " " + str(queryset.created_at) + " " + queryset.purpose + " " + "participant counts : " + str(queryset.participants_count) + " "
            
            full_content += whisper.get_whisper_full_text(queryset,True)
            queryset.full_content = full_content

            if queryset.file_id:
                OpenAIService.delete_file(queryset.file_id)

            pdf = FileService.create_pdf_from_text(full_content)
            file = OpenAIService.upload_file(pdf)
            queryset.file_id = file.id 
            queryset.save()
            # ======== 
            return Response(
                {"message": "Diarization updated successfully", "data": response},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"error": "Invalid diarization data"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class XClassmateQuizViewset(APIView):
    serializer_class = XClassmateQuizSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, xclassmate_id, *args, **kwargs):
        """
        Retrieve a list of quizzes created by the requesting user.

        Returns a list of serialized XclassmateQuiz objects.
        """
        queryset = XClassmateQuiz.objects.filter(xclassmate=xclassmate_id)
        serializer = XClassmateQuizSerializer(queryset, many=True)
        return Response(serializer.data)


class XClassmateToggleIsAddedXBrainView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, xclassmate_id, *args, **kwargs):
        classmate = get_object_or_404(XClassmate, id=xclassmate_id)

        is_added_xbrain = request.data.get('is_added_xbrain', None)
        is_added_report = request.data.get('is_added_report', None)

        if is_added_xbrain is None:
            return Response({"detail": "'is_added_xbrain' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(is_added_xbrain, bool):
            return Response({"detail": "'is_added_xbrain' must be a boolean value."}, status=status.HTTP_400_BAD_REQUEST)

        classmate.is_added_xbrain = is_added_xbrain
        classmate.is_added_report = is_added_report
        classmate.save()

        return Response({

            'is_added_xbrain': classmate.is_added_xbrain,
            'is_added_report': classmate.is_added_report,
        }, status=status.HTTP_200_OK)


class XClassmateCategoryViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, category_id):
        user = self.request.user
        queryset = (
            XClassmate.objects.select_related(
                "unit", "created_by", "category", "sub_category")
            .prefetch_related("participants")
            .annotate(task_count=Count("tasks"))
            .order_by("-created_at")
            .filter(created_by=user, category_id=category_id)
        )
        return queryset.filter(Q(participants=user) | Q(created_by=user))

    def paginate_queryset(self, queryset, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        return paginated_queryset, paginator

    def get(self, request, category_id, *args, **kwargs):
        queryset = self.get_queryset(category_id)
        paginated_queryset, paginator = self.paginate_queryset(
            queryset, request)

        if paginated_queryset is not None:
            serializer = XClassmateListSerializer(
                paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = XClassmateListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
