import logging
from celery import shared_task
from examples.bucket_upload_helper import upload_data_in_bucket
from xmeeting.models import (
    ActionItem,
    EmotionalAnalysis,
    Employee,
    KnowledgeBase,
    QuestionAnswer,
    Recording,
    TechnicalMetadata,
    TopicKeyword,
    XMeeting,
    XMeetingNote,
    XMeetingTranscript,
    XMeetingParticipant,
)

logger = logging.getLogger(__name__)


def upload_action_item_in_bucket():
    action_items = ActionItem.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in action_items:
        data = {
            "action_item_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "description": item.description,
            "assigned_to_employee_id": item.assigned_to.pk if item.assigned_to else None,
            "due_date": item.due_date.strftime("%Y-%m-%d"),
            "status": item.status,
            "priority": item.priority,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="action_item",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading action item (ID {item.pk}) to GCP: {e}")

    ActionItem.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_emotional_analysis_in_bucket():
    emotional_analyses = EmotionalAnalysis.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in emotional_analyses:
        data = {
            "emotional_analysis_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "participant_employee_id": item.participant.pk,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "emotion": item.emotion,
            "emotion_score": item.emotion_score,
            "sentiment": item.sentiment,
            "sentiment_score": item.sentiment_score,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="emotional_analysis",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading emotional analysis (ID {item.pk}) to GCP: {e}"
            )

    EmotionalAnalysis.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_employee_in_bucket():
    employees = Employee.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in employees:
        data = {
            "employee_id": item.pk,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "email": item.email,
            "department": item.department if item.department else None,
            "job_title": item.job_title if item.job_title else None,
            "location": item.location if item.location else None,
            "manager_employee_id": item.manager.pk if item.manager else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="employee",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading employee (ID {item.pk}) to GCP: {e}")

    Employee.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_knowledge_base_in_bucket():
    knowledge_bases = KnowledgeBase.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in knowledge_bases:
        data = {
            "knowledge_base_id": item.pk,
            "source_id": item.source_id,
            "source_type": item.source_type,
            "title": item.title,
            "content": item.content,
            "keywords": item.keywords or [],
            "creation_date": item.creation_date.strftime("%Y-%m-%d"),
            "author_employee_id": item.author.pk if item.author else None,
            "access_level": item.access_level,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="knowledge_base",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading knowledge base (ID {item.pk}) to GCP: {e}")

    KnowledgeBase.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_question_answer_in_bucket():
    question_answers = QuestionAnswer.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in question_answers:
        data = {
            "question_answer_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "question": item.question,
            "answer": item.answer,
            "asked_by_employee_id": item.asked_by.pk,
            "answered_by_employee_id": item.answered_by.pk if item.answered_by else None,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="question_answer",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading question answer (ID {item.pk}) to GCP: {e}")

    QuestionAnswer.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_recording_in_bucket():
    recordings = Recording.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in recordings:
        data = {
            "recording_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "recording_url": item.recording_url,
            "file_format": item.file_format,
            "file_size_mb": item.file_size_mb,
            "duration_minutes": item.duration_minutes,
            "storage_location": item.storage_location,
            "access_level": item.access_level,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="recording",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading recording (ID {item.pk}) to GCP: {e}")

    Recording.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_technical_metadata_in_bucket():
    technical_metadata = TechnicalMetadata.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in technical_metadata:
        data = {
            "technical_metadata_id": item.pk,
            "source_system": item.source_system,
            "data_retrieval_created_at": item.data_retrieval_created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "data_sync_status": item.data_sync_status,
            "api_call_id": item.api_call_id if item.api_call_id else None,
            "processing_notes": (
                item.processing_notes if item.processing_notes else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="technical_metadata",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading technical metadata (ID {item.pk}) to GCP: {e}"
            )

    TechnicalMetadata.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_topic_keyword_in_bucket():
    topic_keywords = TopicKeyword.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in topic_keywords:
        data = {
            "topic_keyword_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "topic_name": item.topic_name,
            "keywords": item.keywords,
            "start_time": item.start_time.strftime("%H:%M:%S"),
            "end_time": item.end_time.strftime("%H:%M:%S"),
            "importance_score": item.importance_score,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="topic_keyword",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading topic keyword (ID {item.pk}) to GCP: {e}")

    TopicKeyword.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_xmeeting_in_bucket():
    xmeetings = XMeeting.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in xmeetings:
        data = {
            "xmeeting_id": item.pk,
            "xmeeting_title": item.xmeeting_title,
            "xmeeting_date": item.xmeeting_date.strftime("%Y-%m-%d"),
            "start_time": item.start_time.strftime("%H:%M:%S"),
            "end_time": item.end_time.strftime("%H:%M:%S"),
            "duration_minutes": item.duration_minutes,
            "organizer_employee_id": item.organizer.pk,
            "xmeeting_type": item.xmeeting_type,
            "platform": item.platform,
            "location": item.location,
            "agenda": item.agenda if item.agenda else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="xmeeting",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading xmeeting (ID {item.pk}) to GCP: {e}")

    XMeeting.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_xmeeting_note_in_bucket():
    xmeeting_notes = XMeetingNote.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in xmeeting_notes:
        data = {
            "xmeeting_note_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "employee_id": item.employee.pk,
            "note_text": item.note_text,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "visibility": item.visibility,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="xmeeting_note",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading xmeeting note (ID {item.pk}) to GCP: {e}")

    XMeetingNote.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_xmeeting_transcript_in_bucket():
    xmeeting_transcripts = XMeetingTranscript.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in xmeeting_transcripts:
        data = {
            "xmeeting_transcript_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "transcript_text": item.transcript_text,
            "language": item.language,  # TODO update this model foreign key
            "confidence_score": (
                item.confidence_score if item.confidence_score else None
            ),
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="xmeeting_transcript",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading xmeeting transcript (ID {item.pk}) to GCP: {e}"
            )

    XMeetingTranscript.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_xmeeting_participant_in_bucket():
    xmeeting_participants = XMeetingParticipant.objects.filter(upload_bucket=False)

    successfully_uploaded = []

    for item in xmeeting_participants:
        data = {
            "xmeeting_participant_id": item.pk,
            "xmeeting_id": item.xmeeting.pk,
            "employee_id": item.employee.pk,
            "role": item.role,
            "attendance_status": item.attendance_status,
            "join_time": item.join_time.strftime("%Y-%m-%d %H:%M:%S") if item.join_time else None,
            "leave_time": (
                item.leave_time.strftime("%Y-%m-%d %H:%M:%S")
                if item.leave_time
                else None
            ),
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="xmeeting",
                model_name="xmeeting_participant",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading xmeeting participant (ID {item.pk}) to GCP: {e}"
            )

    XMeetingParticipant.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


@shared_task
def upload_xmeeting_data_in_bucket():

    upload_action_item_in_bucket()
    upload_emotional_analysis_in_bucket()
    upload_employee_in_bucket()
    upload_knowledge_base_in_bucket()
    upload_question_answer_in_bucket()
    upload_recording_in_bucket()
    upload_technical_metadata_in_bucket()
    upload_topic_keyword_in_bucket()
    upload_xmeeting_in_bucket()
    upload_xmeeting_note_in_bucket()
    upload_xmeeting_transcript_in_bucket()
    upload_xmeeting_participant_in_bucket()
