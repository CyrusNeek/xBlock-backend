import logging
from celery import shared_task
from examples.bucket_upload_helper import upload_data_in_bucket
from vtk.models import (
    VTKUser,
    Recording,
    Transcription,
    GeneratedContent,
    ContentFeedback,
    KnowledgeBase,
    LanguageSupported,
    ContentType,
    ExportedFile,
    TechnicalMetadata
)

logger = logging.getLogger(__name__)

def upload_vtk_user_in_bucket():
    vtk_users = VTKUser.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in vtk_users:
        data = {
            "stk_user_id": item.pk,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "email": item.email,
            "date_joined": item.date_joined.strftime("%Y-%m-%d"),
            "language_preference_language_supported_id": item.language_preference.pk,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="stk_user",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading VTK User (ID {item.pk}) to GCP: {e}")

    VTKUser.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_recording_in_bucket():
    recordings = Recording.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in recordings:
        data = {
            "recording_id": item.pk,
            "stk_user_id": item.user.pk,
            "recording_title": item.recording_title,
            "recording_date": item.recording_date.strftime("%Y-%m-%d"),
            "recording_time": item.recording_time.strftime("%H:%M:%S"),
            "duration_seconds": item.duration_seconds,
            "audio_file_path": item.audio_file_path if item.audio_file_path else None,
            "language_supported_id": item.language.pk,
            "transcription_status": item.transcription_status,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="recording",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Recording (ID {item.pk}) to GCP: {e}")

    Recording.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_transcription_in_bucket():
    transcriptions = Transcription.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in transcriptions:
        data = {
            "transcription_id": item.pk,
            "recording_id": item.recording.pk,
            "transcription_text": item.transcription_text,
            "language_supported_id": item.language.pk,
            "transcription_service": item.transcription_service,
            "confidence_score": item.confidence_score,
            "transcription_date": item.transcription_date.strftime("%Y-%m-%d") if item.transcription_date else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="transcription",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Transcription (ID {item.pk}) to GCP: {e}")

    Transcription.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_generated_content_in_bucket():
    generated_contents = GeneratedContent.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in generated_contents:
        data = {
            "generated_content_id": item.pk,
            "transcription_id": item.transcription.pk,
            "stk_user_id": item.user.pk,
            "content_type_id": item.content_type.pk,
            "language_supported_id": item.language.pk,
            "content_text": item.content_text,
            "generation_date": item.generation_date.strftime("%Y-%m-%d"),
            "generation_time": item.generation_time.strftime("%H:%M:%S"),
            "status": item.status,
            "feedback_provided": item.feedback_provided,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="generated_content",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading GeneratedContent (ID {item.pk}) to GCP: {e}")

    GeneratedContent.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_content_feedback_in_bucket():
    content_feedbacks = ContentFeedback.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in content_feedbacks:
        data = {
            "content_feedback_id": item.pk,
            "content_generated_content_id": item.content.pk,
            "stk_user_id": item.user.pk,
            "feedback_date": item.feedback_date.strftime("%Y-%m-%d"),
            "feedback_time": item.feedback_time.strftime("%H:%M:%S"),
            "rating": item.rating if item.rating else None,
            "comments": item.comments if item.comments else None,
            "improvement_suggestions": item.improvement_suggestions if item.improvement_suggestions else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="content_feedback",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading ContentFeedback (ID {item.pk}) to GCP: {e}")

    ContentFeedback.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_knowledge_base_in_bucket():
    knowledge_bases = KnowledgeBase.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in knowledge_bases:
        data = {
            "knowledge_base_id": item.pk,
            "stk_user_id": item.user.pk,
            "source_content_generated_content_id": item.source_content.pk,
            "title": item.title,
            "content": item.content,
            "language_supported_id": item.language.pk,
            "keywords": item.keywords,
            "creation_date": item.creation_date.strftime("%Y-%m-%d"),
            "approval_status": item.approval_status,
            "approver_stk_user_id": item.approver.pk if item.approver else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="knowledge_base",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading KnowledgeBase (ID {item.pk}) to GCP: {e}")

    KnowledgeBase.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_language_supported_in_bucket():
    languages_supported = LanguageSupported.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in languages_supported:
        data = {
            "language_supported_id": item.pk,
            "language_code": item.language_code,
            "language_name": item.language_name,
            "is_supported": item.is_supported,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="language_supported",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading LanguageSupported (ID {item.pk}) to GCP: {e}")

    LanguageSupported.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_content_type_in_bucket():
    content_types = ContentType.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in content_types:
        data = {
            "content_type_id": item.pk,
            "content_type": item.content_type,
            "description": item.description,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="content_type",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading ContentType (ID {item.pk}) to GCP: {e}")

    ContentType.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_exported_file_in_bucket():
    exported_files = ExportedFile.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in exported_files:
        data = {
            "exported_file_id": item.pk,
            "content_generated_content_id": item.content.pk,
            "stk_user_id": item.user.pk,
            "export_date": item.export_date.strftime("%Y-%m-%d"),
            "export_time": item.export_time.strftime("%H:%M:%S"),
            "file_format": item.file_format,
            "file_path": item.file_path,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="exported_file",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading ExportedFile (ID {item.pk}) to GCP: {e}")

    ExportedFile.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_technical_metadata_in_bucket():
    technical_metadatas = TechnicalMetadata.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in technical_metadatas:
        data = {
            "technical_metadata_id": item.pk,
            "process_name": item.process_name,
            "source_id": item.source_id,
            "status": item.status,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "error_message": item.error_message if item.error_message else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="stk",
                model_name="technical_metadata",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading TechnicalMetadata (ID {item.pk}) to GCP: {e}")

    TechnicalMetadata.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


@shared_task
def upload_vtk_data_to_bucket():
    upload_vtk_user_in_bucket()
    upload_recording_in_bucket()
    upload_transcription_in_bucket()
    upload_generated_content_in_bucket()
    upload_content_feedback_in_bucket()
    upload_knowledge_base_in_bucket()
    upload_language_supported_in_bucket()
    upload_content_type_in_bucket()
    upload_exported_file_in_bucket()
    upload_technical_metadata_in_bucket()
