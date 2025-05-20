from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination


from roles.constants import (
    ACTIVE_MEETING_ACCESS,
    LIMITED_MEETING_ACCESS,
    UNLIMITED_MEETING_ACCESS,
)
from roles.models import Role
from web.models import MeetingQuiz, Meeting
from web.models.category import Category
from web.services.google_bucket import GoogleBucket
from web.services.storage_service import StorageService
from web.tasks.task_meeting import create_meeting_participants
from web.services.whisper import Whisper
from ..models import Meeting, Unit, User, MeetingFile
from ..serializers import (
    MeetingSerializer,
    UpdateDiarizationRequestSerializer,
    MeetingQuizSerializer,
    MeetingListSerializer,
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

from web.signals import signal_trigger_meeting_summarize
from vtk.services import upload_file_to_gcs
from web.services.openai_service import OpenAIService
from web.services.file_service import FileService


logger = logging.getLogger(__name__)

class MeetingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return MeetingListSerializer
        else:
            return MeetingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Meeting.objects.select_related("unit", "created_by")
            .prefetch_related("participants")
            .annotate(task_count=Count("tasks"))
            .order_by("-created_at")
            .filter(created_by=user)
        )

        # THIS PERMISSIONS HAS APPLYED TO MEETING ANALYTICS. NOT MEETING ACCESS
        # user_has_limited_access = UserPermission.check_user_permission(
        #     user, LIMITED_MEETING_ACCESS
        # )
        # user_has_unlimited_access = UserPermission.check_user_permission(
        #     user, UNLIMITED_MEETING_ACCESS
        # )

        # if user_has_limited_access:
        #     return queryset.filter(unit__in=user.all_units)

        # if user_has_unlimited_access:
        #     return queryset.filter(unit__brand__in=user.brands.all())

        return queryset.filter(Q(participants=user) | Q(created_by=user))

    def get_presigned_post_url(self, user, meeting_id):
        file_name = f"meetings/{user.first_name}_{meeting_id}.wav".replace(" ", "_")
        presigned_post = StorageService().generate_presigned_upload_url(file_name)

        logger.info(presigned_post)

        return presigned_post

    def check_permission(self):
        return UserPermission.check_user_permission(
            self.request.user, ACTIVE_MEETING_ACCESS
        )

    def perform_permissions_check(self, request):
        if not self.check_permission():
            raise PermissionDenied("You don't have permission to perform this action.")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = MeetingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MeetingListSerializer(queryset, many=True)
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

        meeting_data = serializer.validated_data

        meeting_data["purpose"] = request.data.get("purpose", "")
        meeting_data["unit"] = user.unit or user.units.first()
        meeting_data["category"] = self.get_category(request.data.get("category"))
        meeting_data["sub_category"] = self.get_category(request.data.get("sub_category"))

        # Fix date fields to handle empty strings
        start_date = request.data.get("start_date", None)
        meeting_data["start_date"] = None if start_date == "" else start_date
        
        end_date = request.data.get("end_date", None)
        meeting_data["end_date"] = None if end_date == "" else end_date
        
        meeting_data["timezone"] = request.data.get("timezone", None)
        repeat_period = request.data.get("repeat_period", None)
        meeting_data["repeat_period"] = None if repeat_period == "" else repeat_period

        meeting_data["held_type"] = request.data.get("held_type", None)

        meeting = serializer.save()

        file_ids = request.data.get("file_ids", None)
        if file_ids:
            for file_id in file_ids:
                try:
                    meeting_file = MeetingFile.objects.filter(id=file_id).first()
                    meeting_file.meeting = meeting
                    meeting_file.save()
                except :
                    print(f"no file exist with id {file_id}")

        meeting.filename = f"meetings/{user.first_name}_{meeting.id}.wav".replace(
            " ", "_"
        )
        uploaded_file = request.FILES.get("file")
        meeting_data = serializer.data
        meeting.save()

        if uploaded_file:
            presigned_url, data = self.get_presigned_post_url(
                user, meeting.id)
            meeting.recording_file_url = presigned_url
            
            uploaded = upload_file_to_gcs(presigned_url,data, uploaded_file)
            if not uploaded:
                return Response(
                    {"error": f"failed to upload file"},
                    status=400  
                )


            meeting.recording_file_url = presigned_url

            meeting.uploaded = True
            meeting_data["presigned_post_data"] = data
            meeting.save()

            signal_trigger_meeting_summarize(Meeting, meeting, True)




        return Response(meeting_data)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        user = request.user
        meeting_data = serializer.validated_data

        meeting_data["purpose"] = request.data.get("purpose", instance.purpose)
        meeting_data["unit"] = user.unit or user.units.first()
        meeting_data["category"] = self.get_category(request.data.get("category", instance.category))
        meeting_data["sub_category"] = self.get_category(request.data.get("sub_category", instance.sub_category))
        
        meeting_data["start_date"] = request.data.get("start_date", instance.start_date)
        meeting_data["end_date"] = request.data.get("end_date", instance.end_date)
        meeting_data["timezone"] = request.data.get("timezone", instance.timezone)
        meeting_data["repeat_period"] = request.data.get("repeat_period", instance.repeat_period)
        meeting_data["held_type"] = request.data.get("held_type", instance.held_type)

        meeting = serializer.save()

        file_ids = request.data.get("file_ids", None)
        if file_ids:
            for file_id in file_ids:
                try:
                    meeting_file = MeetingFile.objects.filter(id=file_id).first()
                    if meeting_file:
                        meeting_file.meeting = meeting
                        meeting_file.save()
                except Exception as e:
                    print(f"Error attaching file {file_id}: {str(e)}")

        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            presigned_url, data = self.get_presigned_post_url(user, meeting.id)
            meeting.recording_file_url = presigned_url

            uploaded = upload_file_to_gcs(presigned_url, data, uploaded_file)
            if not uploaded:
                return Response(
                    {"error": "Failed to upload file"},
                    status=400
                )

            meeting.recording_file_url = presigned_url
            meeting.uploaded = True
            meeting.save()

            signal_trigger_meeting_summarize(Meeting, meeting, True)

        return Response(serializer.data)


    def get_presigned_get_url(self, file_name):
        presigned_url = StorageService().generate_presigned_download_url(file_name)

        return presigned_url

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Serialize meeting data
        meeting_data = MeetingSerializer(instance).data

        # Generate a pre-signed URL for the WAV file if available
        if instance.filename:
            presigned_url = self.get_presigned_get_url(instance.filename)
            meeting_data["presigned_url"] = presigned_url

        return Response(meeting_data)


class WhisperDataView(APIView):
    
    def check_permission(self):
        return UserPermission.check_user_permission(
            self.request.user, ACTIVE_MEETING_ACCESS
        )

    def get(self, request, meeting_id, *args, **kwargs):
        page_size = request.GET.get("page_size", 10)
        page = request.GET.get("page", 1)
        
        whisper = Whisper()
        response = whisper.retrieve_user_voice(
            user_id=request.user.id,
            meeting_id=meeting_id,
            page_size=int(page_size),
            page_number=int(page),
        )
        return Response(response)


            
    @extend_schema(request=UpdateDiarizationRequestSerializer, tags=["meetings"])
    def put(self, request, meeting_id, *args, **kwargs):
        # Retrieve the meeting created by the user with the given primary key
        queryset = Meeting.objects.filter(
            created_by=request.user, id=meeting_id
        ).first()

        # Check and update the speakers in the diarization field
        serializer = UpdateDiarizationRequestSerializer(data=request.data)

        if queryset and serializer.is_valid(raise_exception=True):
            if "new_speaker" in request.data and request.data["new_speaker"] != "":
                serializer.validated_data["user_name"] = request.data["new_speaker"]
            else:
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
                serializer.validated_data["user_name"] = f"{new_user.full_name}"
                create_meeting_participants(new_user.pk, queryset.pk)
            whisper = Whisper()
            response = whisper.update_speaker_name(
                user_id=queryset.created_by.id,
                meeting_id=queryset.id,
                payload=dict(serializer.validated_data),
            )

            #==== update pdf after renaming speaker ====
            full_content = queryset.name + " " + str(queryset.created_at) + " " + queryset.purpose + " " + "participant counts : " + str(queryset.participants_count) + " "

            full_content += whisper.get_whisper_full_text(queryset,False)
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


class MeetingQuizViewset(APIView):
    serializer_class = MeetingQuizSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, meeting_id, *args, **kwargs):
        """
        Retrieve a list of quizzes created by the requesting user.

        Returns a list of serialized MeetingQuiz objects.
        """
        queryset = MeetingQuiz.objects.filter(meeting=meeting_id)
        serializer = MeetingQuizSerializer(queryset, many=True)
        return Response(serializer.data)



class MeetingCategoryViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, category_id):
        user = self.request.user
        queryset = (
            Meeting.objects.select_related("unit", "created_by", "category", "sub_category")
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
        paginated_queryset, paginator = self.paginate_queryset(queryset, request)

        if paginated_queryset is not None:
            serializer = MeetingListSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MeetingListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
