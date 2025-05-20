import logging
from celery import shared_task
from examples.bucket_upload_helper import upload_data_in_bucket
from employee.models import (
    Conversation,
    Department,
    EmergencyContact,
    EmotionalAnalysis,
    Employee,
    EmploymentDetail,
    KnowledgeBaseContribution,
    Manager,
    PerformanceRecord,
    PersonalInformation,
    TechnicalMetaData,
    TrainingAndDevelopment,
    VoiceInteraction
)

logger = logging.getLogger(__name__)


def upload_conversation_in_bucket():
    conversations = Conversation.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in conversations:
        data = {
            "conversation_id": item.pk,
            "employee_id": item.employee.pk,
            "conversation_date": item.conversation_date.strftime("%Y-%m-%d"),
            "conversation_time": item.conversation_time.strftime("%H:%M:%S.%f"),
            "conversation_type": item.conversation_type,
            "participants": item.participants,
            "content": item.content if item.content else None,
            "language": item.language,
            "sentiment": item.sentiment if item.sentiment else None,
            "sentiment_score": item.sentiment_score if item.sentiment_score else None,
            "topics": item.topics if item.topics else None,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="conversation",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Conversation (ID {item.pk}) to GCP: {e}")

    Conversation.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_department_in_bucket():
    departments = Department.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in departments:
        data = {
            "department_id": item.pk,
            "department_name": item.department_name,
            "description": item.description if item.description else None,
            "parent_department_id": item.parent.pk if item.parent else None,
            "manager_id": item.manager.pk if item.manager else None,
            "location": item.location if item.location else None,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="department",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Department (ID {item.pk}) to GCP: {e}")

    Department.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_emergency_contact_in_bucket():
    emergency_contacts = EmergencyContact.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in emergency_contacts:
        data = {
            "emergency_contact_id": item.pk,
            "employee_id": item.employee.pk,
            "contact_name": item.contact_name,
            "relationship": item.relationship,
            "contact_phone": item.contact_phone,
            "contact_email": item.contact_email if item.contact_email else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="emergency_contact",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Emergency Contact (ID {item.pk}) to GCP: {e}")

    EmergencyContact.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_emotional_analysis_in_bucket():
    emotional_analyses = EmotionalAnalysis.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in emotional_analyses:
        data = {
            "emotional_analysis_id": item.pk,
            "voice_interaction_id": item.interaction.pk,
            "employee_id": item.employee.pk,
            "analysis_created_at": item.analysis_created_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "emotion": item.emotion,
            "emotion_score": item.emotion_score,
            "sentiment": item.sentiment,
            "sentiment_score": item.sentiment_score,
            "additional_insights": item.additional_insights if item.additional_insights else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="emotional_analysis",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Emotional Analysis (ID {item.pk}) to GCP: {e}")

    EmotionalAnalysis.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_employee_in_bucket():
    employees = Employee.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in employees:
        data = {
            "employee_id": item.pk,
            "first_name": item.first_name if item.first_name else None,
            "last_name": item.last_name if item.last_name else None,
            "full_name": item.full_name if item.full_name else None,
            "preferred_name": item.preferred_name if item.preferred_name else None,
            "email": item.email,
            "phone_number": item.phone_number,
            "department_id": item.department.pk if item.department else None,
            "manager_employee_id": item.manager.pk if item.manager else None,
            "employment_status": item.employment_status,
            "employment_start_date": item.employment_start_date.strftime("%Y-%m-%d"),
            "employment_end_date": item.employment_end_date.strftime("%Y-%m-%d %H:%M:%S.%f") if item.employment_end_date else None,
            "location": item.location if item.location else None,
            "job_title": item.job_title if item.job_title else None,
            "employee_tags": item.employee_tags if item.employee_tags else [],
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="employee",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Employee (ID {item.pk}) to GCP: {e}")

    Employee.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_employment_detail_in_bucket():
    employment_details = EmploymentDetail.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in employment_details:
        data = {
            "employment_detail_id": item.pk,
            "employee_id": item.employee.pk,
            "employment_type": item.employment_type if item.employment_type else None,
            "work_schedule": item.work_schedule if item.work_schedule else None,
            "salary": item.salary if item.salary else None,
            "pay_frequency": item.pay_frequency if item.pay_frequency else None,
            "benefits_enrolled": item.benefits_enrolled or [],
            "last_promotion_date": item.last_promotion_date.strftime("%Y-%m-%d") if item.last_promotion_date else None,
            "performance_score": item.performance_score if item.performance_score is not None else None,
            "bonus_eligibility": item.bonus_eligibility,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="employment_detail",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading EmploymentDetail (ID {item.pk}) to GCP: {e}")

    EmploymentDetail.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_knowledge_base_contribution_in_bucket():
    contributions = KnowledgeBaseContribution.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in contributions:
        data = {
            "knowledge_base_contribution_id": item.pk,
            "employee_id": item.employee.pk,
            "contribution_date": item.contribution_date.strftime("%Y-%m-%d"),
            "content_type": item.content_type,
            "title": item.title,
            "description": item.description,
            "content_uri": item.content_uri if item.content_uri else None,
            "keywords": item.keywords if item.keywords else [],
            "views_count": item.views_count if item.views_count else None,
            "likes_count": item.likes_count if item.likes_count else None,
            "comments_count": item.comments_count if item.comments_count else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="knowledge_base_contribution",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading KnowledgeBaseContribution (ID {item.pk}) to GCP: {e}")

    KnowledgeBaseContribution.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_manager_in_bucket():
    managers = Manager.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in managers:
        data = {
            "manager_id": item.pk,
            "manager_level": item.manager_level if item.manager_level else None,
            "employee_id": item.employee.pk if item.employee else None,
            "reports_to_manager_id": item.reports_to if item.reports_to else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="manager",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Manager (ID {item.pk}) to GCP: {e}")

    Manager.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_performance_record_in_bucket():
    performance_records = PerformanceRecord.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in performance_records:
        data = {
            "performance_record_id": item.pk,
            "employee_id": item.employee.pk,
            "evaluation_date": item.evaluation_date.strftime("%Y-%m-%d"),
            "evaluator_id": item.evaluator_id,
            "performance_score": item.performance_score,
            "performance_rating": item.performance_rating,
            "goals": item.goals,
            "feedback": item.feedback,
            "employee_comments": item.employee_comments if item.employee_comments else None,
            "action_items": item.action_items,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="performance_record",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading PerformanceRecord (ID {item.pk}) to GCP: {e}")

    PerformanceRecord.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_personal_information_in_bucket():
    personal_informations = PersonalInformation.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in personal_informations:
        data = {
            "personal_information_id": item.pk,
            "employee_id": item.employee.pk,
            "birthdate": item.birthdate.strftime("%Y-%m-%d"),
            "gender": item.gender,
            "marital_status": item.marital_status,
            "nationality": item.nationality,
            "address": item.address,
            "city": item.city,
            "state": item.state,
            "zip_code": item.zip_code,
            "country": item.country,
            "personal_email": item.personal_email,
            "personal_phone": item.personal_phone,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="personal_information",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading PersonalInformation (ID {item.pk}) to GCP: {e}")

    PersonalInformation.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_technical_metadata_in_bucket():
    technical_metadatas = TechnicalMetaData.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in technical_metadatas:
        data = {
            "technical_meta_data_id": item.pk,
            "source_system": item.source_system,
            "data_retrieval_created_at": item.data_retrieval_created_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "data_sync_status": item.data_sync_status,
            "api_call": item.api_call,
            "processing_notes": item.processing_notes if item.processing_notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="technical_metadata",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading TechnicalMetaData (ID {item.pk}) to GCP: {e}")

    TechnicalMetaData.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_training_and_development_in_bucket():
    training_and_developments = TrainingAndDevelopment.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in training_and_developments:
        data = {
            "training_and_development_id": item.pk,
            "employee_id": item.employee.pk,
            "training_name": item.training_name,
            "training_type": item.training_type,
            "provider": item.provider,
            "start_date": item.start_date.strftime("%Y-%m-%d"),
            "end_date": item.end_date.strftime("%Y-%m-%d") if item.end_date else None,
            "completion_status": item.completion_status,
            "certification_received": item.certification_received,
            "certificate_id": item.certificate_id if item.certificate_id else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="training_and_development",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading TrainingAndDevelopment (ID {item.pk}) to GCP: {e}")

    TrainingAndDevelopment.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_voice_interaction_in_bucket():
    voice_interactions = VoiceInteraction.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in voice_interactions:
        data = {
            "voice_interaction_id": item.pk,
            "employee_id": item.employee.pk,
            "interaction_date": item.interaction_date.strftime("%Y-%m-%d"),
            "interaction_time": item.interaction_time.strftime("%H:%M:%S.%f"),
            "duration_seconds": item.duration_seconds,
            "interaction_type": item.interaction_type,
            "participants": item.participants if item.participants else [],
            "transcript": item.transcript if item.transcript else None,
            "audio_file_path": item.audio_file_path,
            "language": item.language,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="employee",
                model_name="voice_interaction",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading VoiceInteraction (ID {item.pk}) to GCP: {e}")

    VoiceInteraction.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


@shared_task
def upload_employee_data_in_bucket():
    
    upload_employee_in_bucket()
    upload_department_in_bucket()
    upload_conversation_in_bucket()
    upload_emergency_contact_in_bucket()
    upload_emotional_analysis_in_bucket()
    upload_employment_detail_in_bucket()
    upload_knowledge_base_contribution_in_bucket()
    upload_manager_in_bucket()
    upload_performance_record_in_bucket()
    upload_personal_information_in_bucket()
    upload_technical_metadata_in_bucket()
    upload_training_and_development_in_bucket()
    upload_voice_interaction_in_bucket()