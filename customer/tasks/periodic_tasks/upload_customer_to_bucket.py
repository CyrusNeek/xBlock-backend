import logging
from celery import shared_task
from examples.bucket_upload_helper import upload_data_in_bucket
from customer.models import (
    Address,
    AIInteractionMetadata,
    CompetitiveAnalysis,
    ContactInformation,
    CustomerCommunication,
    CustomerDemographic,
    CustomerEnrichmentData,
    CustomerFeedback,
    CustomerLifetimeValue,
    CustomerLocationBehavior,
    CustomerSegmentation,
    Customer,
    ItemPurchased,
    LeadSource,
    LoyaltyProgram,
    MarketingPreference,
    NoteAndActivity,
    PurchaseAssistantRecord,
    PurchaseHistory,
    SocialMediaProfile,
    SupportAssistantRecord,
    SupportTicket,
    TechnicalMetaData,
    TradeAreaAnalysis,
    WebsiteInteraction,
    XBrainCustomerInteraction,
    XBrainConversationLog,
)

logger = logging.getLogger(__name__)


def upload_address_in_bucket():
    addresses = Address.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in addresses:
        data = {
            "address_id": item.pk,
            "customer_id": item.customer.pk,
            "address_type": item.address_type,
            "street_address": item.street_address,
            "city": item.city,
            "state": item.state,
            "zip_code": item.zip_code,
            "country": item.country,
            "is_primary": item.is_primary,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="address",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Address (ID {item.pk}) to GCP: {e}")

    Address.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_ai_interaction_metadata_in_bucket():
    metadata = AIInteractionMetadata.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in metadata:
        data = {
            "ai_interaction_metadata_id": item.pk,
            "xbrain_customer_interaction_id": item.interaction_id.pk,
            "processing_time_ms": item.processing_time_ms,
            "confidence_score": item.confidence_score,
            "ai_model_version": item.ai_model_version,
            "language_model": item.language_model,
            "error_codes": item.error_codes if item.error_codes else [],
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="ai_interaction_metadata",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading AIInteractionMetadata (ID {item.pk}) to GCP: {e}"
            )

    AIInteractionMetadata.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_competitive_analysis_in_bucket():
    analyses = CompetitiveAnalysis.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in analyses:
        data = {
            "competitive_analysis_id": item.pk,
            "customer_id": item.customer.pk,
            "competitor": item.competitor,
            "competitor_name": item.competitor_name,
            "visit_date": item.visit_date.strftime("%Y-%m-%d"),
            "visit_time": item.visit_time.strftime("%H:%M:%S"),
            "visit_frequency": item.visit_frequency,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="competitive_analysis",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading CompetitiveAnalysis (ID {item.pk}) to GCP: {e}"
            )

    CompetitiveAnalysis.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_contact_information_in_bucket():
    contact_info = ContactInformation.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in contact_info:
        data = {
            "contact_information_id": item.pk,
            "customer_id": item.customer.pk,
            "contact_type": item.contact_type,
            "contact_value": item.contact_value,
            "is_primary": item.is_primary,
            "opt_in_status": item.opt_in_status,
            "verification_status": item.verification_status,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="contact_information",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading ContactInformation (ID {item.pk}) to GCP: {e}"
            )

    ContactInformation.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_customer_in_bucket():
    customers = Customer.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in customers:
        data = {
            "customer_id": item.pk,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "date_of_birth": item.date_of_birth.strftime("%Y-%m-%d"),
            "gender": item.gender,
            "preferred_language": item.preferred_language,
            "customer_since": item.customer_since.strftime("%Y-%m-%d"),
            "status": item.status,
            "customer_segmentation_id": item.segment_id.pk,
            "loyalty_program_id": item.loyalty_program_id.pk,
            "lifetime_value": item.lifetime_value,
            "notes": item.notes if item.notes is not None else None,
            "ai_interaction_consent": item.ai_interaction_consent,
            "data_enriched": item.data_enriched
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading Customer (ID {item.pk}) to GCP: {e}")

    Customer.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_customer_communication_in_bucket():
    communications = CustomerCommunication.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in communications:
        data = {
            "customer_communication_id": item.pk,
            "customer_id": item.customer.pk,
            "communication_type": item.communication_type,
            "subject": item.subject,
            "content": item.content,
            "communication_date": item.communication_date.strftime("%Y-%m-%d"),
            "communication_time": item.communication_time.strftime("%H:%M:%S.%f"),
            "employee_id": item.employee_id if item.employee_id else None,
            "channel": item.channel,
            "response_required": item.response_required,
            "response_status": item.response_status,
            "notes": item.notes if item.notes else None,
            "handled_by": item.handled_by,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer_communication",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading CustomerCommunication (ID {item.pk}) to GCP: {e}"
            )

    CustomerCommunication.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_customer_feedback_in_bucket():
    feedbacks = CustomerFeedback.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in feedbacks:
        data = {
            "customer_feedback_id": item.pk,
            "customer_id": item.customer.pk,
            "feedback_date": item.feedback_date.strftime("%Y-%m-%d"),
            "feedback_time": item.feedback_time.strftime("%H:%M:%S.%f"),
            "channel": item.channel,
            "rating": item.rating,
            "comments": item.comments,
            "response_status": item.response_status,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer_feedback",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading CustomerFeedback (ID {item.pk}) to GCP: {e}")

    CustomerFeedback.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_customer_enrichment_data_in_bucket():
    enrichment_data = CustomerEnrichmentData.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in enrichment_data:
        data = {
            "customer_enrichment_data_id": item.pk,
            "customer_id": item.customer.pk,
            "additional_phones": item.additional_phones or [],
            "additional_emails": item.additional_emails or [],
            "social_media_handles": item.social_media_handles or [],
            "interests": item.interests or [],
            "purchasing_behaviour": item.purchasing_behaviour,
            "data_source": item.data_source,
            "data_retrieval": item.data_retrieval.strftime("%Y-%m-%d"),
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer_enrichment_data",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading CustomerEnrichmentData (ID {item.pk}) to GCP: {e}"
            )

    CustomerEnrichmentData.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_customer_lifetime_value_in_bucket():
    lifetime_values = CustomerLifetimeValue.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in lifetime_values:
        data = {
            "customer_lifetime_value_id": item.pk,
            "customer_id": item.customer.pk,
            "calculation_date": item.calculation_date.strftime("%Y-%m-%d"),
            "total_revenue": item.total_revenue,
            "total_cost": item.total_cost,
            "clv": item.clv,
            "clv_model": item.clv_model,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer_lifetime_value",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading CustomerLifetimeValue (ID {item.pk}) to GCP: {e}"
            )

    CustomerLifetimeValue.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_customer_segmentation_in_bucket():
    segmentations = CustomerSegmentation.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in segmentations:
        data = {
            "customer_segmentation_id": item.pk,
            "segment_name": item.segment_name,
            "description": item.description,
            "criteria": item.criteria,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer_segmentation",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading CustomerSegmentation (ID {item.pk}) to GCP: {e}"
            )

    CustomerSegmentation.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_lead_source_in_bucket():
    lead_sources = LeadSource.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in lead_sources:
        data = {
            "lead_source_id": item.pk,
            "customer_id": item.customer.pk,
            "source_type": item.source_type,
            "source_details": item.source_details,
            "acquisition_date": item.acquisition_date.strftime("%Y-%m-%d"),
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="lead_source",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading LeadSource (ID {item.pk}) to GCP: {e}")

    LeadSource.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_loyalty_program_in_bucket():
    loyalty_programs = LoyaltyProgram.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in loyalty_programs:
        data = {
            "loyalty_program_id": item.pk,
            "customer_id": item.customer.pk,
            "program_name": item.program_name,
            "enrollment_date": item.enrollment_date.strftime("%Y-%m-%d"),
            "loyalty_points": item.loyalty_points,
            "membership_level": item.membership_level,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="loyalty_program",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading LoyaltyProgram (ID {item.pk}) to GCP: {e}")

    LoyaltyProgram.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_marketing_preference_in_bucket():
    marketing_preferences = MarketingPreference.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in marketing_preferences:
        data = {
            "marketing_preference_id": item.pk,
            "customer_id": item.customer.pk,
            "communication_channel": item.communication_channel,
            "opt_in_status": item.opt_in_status,
            "opt_in_date": item.opt_in_date.strftime("%Y-%m-%d") if item.opt_in_date else None,
            "opt_out_date": item.opt_out_date.strftime("%Y-%m-%d") if item.opt_out_date else None,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="marketing_preference",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading MarketingPreference (ID {item.pk}) to GCP: {e}"
            )

    MarketingPreference.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_note_and_activities_in_bucket():
    notes_and_activities = NoteAndActivity.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in notes_and_activities:
        data = {
            "note_and_activity_id": item.pk,
            "customer_id": item.customer.pk,
            "employee": item.employee,
            "activity_type": item.activity_type,
            "activity_date": item.activity_date.strftime("%Y-%m-%d"),
            "activity_time": item.activity_time.strftime("%H:%M:%S.%f"),
            "subject": item.subject,
            "description": item.description,
            "status": item.status,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="note_and_activity",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading NoteAndActivity (ID {item.pk}) to GCP: {e}"
            )

    NoteAndActivity.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_purchase_history_in_bucket():
    purchase_histories = PurchaseHistory.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in purchase_histories:
        data = {
            "purchase_history_id": item.pk,
            "customer_id": item.customer.pk,
            "order_id": item.order_id,
            "purchase_date": item.purchase_date.strftime("%Y-%m-%d"),
            "purchase_time": item.purchase_time.strftime("%H:%M:%S.%f"),
            "items_purchased_id": item.items_purchased.pk,
            "total_amount": item.total_amount,
            "payment_method": item.payment_method,
            "transaction_status": item.transaction_status,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="purchase_history",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading PurchaseHistory (ID {item.pk}) to GCP: {e}")

    PurchaseHistory.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_social_media_profile_in_bucket():
    social_media_profiles = SocialMediaProfile.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in social_media_profiles:
        data = {
            "social_media_profile_id": item.pk,
            "customer_id": item.customer.pk,
            "platform": item.platform,
            "profile_url": item.profile_url,
            "username": item.username,
            "is_connected": item.is_connected,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="social_media_profile",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading SocialMediaProfile (ID {item.pk}) to GCP: {e}"
            )

    SocialMediaProfile.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_support_assistant_record_in_bucket():
    support_assistant_records = SupportAssistantRecord.objects.filter(
        upload_bucket=False
    )
    successfully_uploaded = []

    for item in support_assistant_records:
        data = {
            "support_assistant_record_id": item.pk,
            "xbrain_customer_interaction_id": item.interaction.pk,
            "customer_id": item.customer.pk,
            "issue_reported": item.issue_reported,
            "resolution_provided": item.resolution_provided,
            "resolution_status": item.resolution_status,
            "escalation_support_ticket_id": item.escalation_ticket_id.pk if item.escalation_ticket_id else None,
            "resolution_time": item.resolution_time,
            "customer_satisfaction": item.customer_satisfaction,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="support_assistant_record",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading SupportAssistantRecord (ID {item.pk}) to GCP: {e}"
            )

    SupportAssistantRecord.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_technical_metadata_in_bucket():
    technical_metadata = TechnicalMetaData.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in technical_metadata:
        data = {
            "technical_metadata_id": item.pk,
            "source_system": item.source_system,
            "data_retrieval_created_at": item.data_retrieval_created_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "data_sync_status": item.data_sync_status,
            "api_call_id": item.api_call_id if item.api_call_id is not None else None,
            "processing_notes": item.processing_notes if item.processing_notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="technical_metadata",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading TechnicalMetaData (ID {item.pk}) to GCP: {e}"
            )

    TechnicalMetaData.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_trade_area_analysis_in_bucket():
    trade_area_analyses = TradeAreaAnalysis.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in trade_area_analyses:
        data = {
            "trade_area_analysis_id": item.pk,
            "customer_id": item.customer.pk,
            "home_zip_code": item.home_zip_code,
            "work_zip_code": item.work_zip_code,
            "distance_to_store": item.distance_to_store,
            "commute_patterns": item.commute_patterns,
            "trade_area_latitude": item.trade_area_latitude,
            "trade_area_longitude": item.trade_area_longitude,
            "data_source": item.data_source,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="trade_area_analysis",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading TradeAreaAnalysis (ID {item.pk}) to GCP: {e}"
            )

    TradeAreaAnalysis.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_customer_location_behavior_in_bucket():
    customer_location_behaviors = CustomerLocationBehavior.objects.filter(
        upload_bucket=False
    )
    successfully_uploaded = []

    for item in customer_location_behaviors:
        data = {
            "customer_location_behavior_id": item.pk,
            "customer_id": item.customer.pk,
            "location": item.location,
            "visit_date": item.visit_date.strftime("%Y-%m-%d"),
            "visit_time": item.visit_time.strftime("%H:%M:%S.%f"),
            "visit_duration_minutes": item.visit_duration_minutes,
            "visit_frequency": item.visit_frequency,
            "location_type": item.location_type,
            "location_name": item.location_name,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "data_source": item.data_source,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer_location_behavior",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading CustomerLocationBehavior (ID {item.pk}) to GCP: {e}"
            )

    CustomerLocationBehavior.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_website_interaction_in_bucket():
    website_interactions = WebsiteInteraction.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in website_interactions:
        data = {
            "website_interaction_id": item.pk,
            "customer_id": item.customer.pk,
            "session_id": item.session_id,
            "page_url": item.page_url,
            "interaction_type": item.interaction_type,
            "interaction_date": item.interaction_date.strftime("%Y-%m-%d"),
            "interaction_time": item.interaction_time.strftime("%H:%M:%S.%f"),
            "device_type": item.device_type,
            "browser": item.browser,
            "ip_address": item.ip_address,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="website_interaction",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading WebsiteInteraction (ID {item.pk}) to GCP: {e}"
            )

    WebsiteInteraction.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_customer_demographic_in_bucket():
    customer_demographics = CustomerDemographic.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in customer_demographics:
        data = {
            "customer_demographic_id": item.pk,
            "customer_id": item.customer.pk,
            "age": item.age,
            "gender": item.gender,
            "income_range": item.income_range,
            "education_level": item.education_level if item.education_level else None,
            "marital_status": item.marital_status if item.marital_status else None,
            "homeowner_status": item.homeowner_status if item.homeowner_status else None,
            "number_of_children": item.number_of_children,
            "occupation": item.occupation,
            "ethnicity": item.ethnicity,
            "language_preference": item.language_preference,
            "data_source": item.data_source,
            "data_retrieval_date": item.data_retrieval_date.strftime("%Y-%m-%d"),
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="customer_demographic",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading CustomerDemographic (ID {item.pk}) to GCP: {e}"
            )

    CustomerDemographic.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_support_ticket_in_bucket():
    support_tickets = SupportTicket.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in support_tickets:
        data = {
            "support_ticket_id": item.pk,
            "customer_id": item.customer.pk,
            "issue_type": item.issue_type,
            "subject": item.subject,
            "description": item.description if item.description is not None else None,
            "ticket_status": item.ticket_status,
            "priority": item.priority,
            "created_date": item.created_date.strftime("%Y-%m-%d"),
            "resolved_date": item.resolved_date.strftime("%Y-%m-%d") if item.resolved_date else None,
            "assigned_to": item.assigned_to if item.assigned_to is not None else None,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="support_ticket",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading SupportTicket (ID {item.pk}) to GCP: {e}")

    SupportTicket.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_xbrain_customer_interaction_in_bucket():
    xbrain_customer_interactions = XBrainCustomerInteraction.objects.filter(
        upload_bucket=False
    )
    successfully_uploaded = []

    for item in xbrain_customer_interactions:
        data = {
            "xbrain_customer_interaction_id": item.pk,
            "customer_id": item.customer.pk,
            "interaction_date": item.interaction_date.strftime("%Y-%m-%d"),
            "interaction_time": item.interaction_time.strftime("%H:%M:%S.%f"),
            "interaction_type": item.interaction_type,
            "channel": item.channel,
            "interaction_status": item.interaction_status,
            "outcome": item.outcome,
            "employee": item.employee if item.employee is not None else None,
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="xbrain_customer_interaction",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading XBrainCustomerInteraction (ID {item.pk}) to GCP: {e}"
            )

    XBrainCustomerInteraction.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_xbrain_conversation_log_in_bucket():
    xbrain_conversation_logs = XBrainConversationLog.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in xbrain_conversation_logs:
        data = {
            "xbrain_conversation_log_id": item.pk,
            "xbrain_customer_interaction_id": item.interaction.pk,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "sender": item.sender,
            "message": item.message,
            "language": item.language,
            "sentiment": item.sentiment,
            "sentiment_score": item.sentiment_score,
            "intent": item.intent,
            "entities": item.entities if item.entities else [],
            "notes": item.notes if item.notes is not None else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="xbrain_conversation_log",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading XBrainConversationLog (ID {item.pk}) to GCP: {e}"
            )

    XBrainConversationLog.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_purchase_assistant_record_in_bucket():
    purchase_assistant_records = PurchaseAssistantRecord.objects.filter(
        upload_bucket=False
    )
    successfully_uploaded = []

    for item in purchase_assistant_records:
        data = {
            "purchase_assistant_record_id": item.pk,
            "xbrain_customer_interaction_id": item.interaction.pk,
            "customer_id": item.customer.pk,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "recommendation_reason": item.recommendation_reason,
            "purchase_decision": item.purchase_decision,
            "purchase_date": item.purchase_date.strftime("%Y-%m-%d") if item.purchase_date else None,
            "purchase_history_id": item.purchase.pk if item.purchase else None,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="purchase_assistant_record",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(
                f"Error uploading PurchaseAssistantRecord (ID {item.pk}) to GCP: {e}"
            )

    PurchaseAssistantRecord.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_item_purchased_in_bucket():
    items_purchased = ItemPurchased.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in items_purchased:
        data = {
            "item_purchased_id": item.pk,
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="customer",
                model_name="item_purchased",
            )
            successfully_uploaded.append(item.pk)
        except Exception as e:
            logger.error(f"Error uploading ItemPurchased (ID {item.pk}) to GCP: {e}")

    ItemPurchased.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )

@shared_task
def upload_customer_data_in_bucket():

    upload_address_in_bucket()
    upload_ai_interaction_metadata_in_bucket()
    upload_competitive_analysis_in_bucket()
    upload_contact_information_in_bucket()
    upload_customer_in_bucket()
    upload_customer_communication_in_bucket()
    upload_customer_feedback_in_bucket()
    upload_customer_enrichment_data_in_bucket()
    upload_customer_lifetime_value_in_bucket()
    upload_customer_segmentation_in_bucket()
    upload_support_ticket_in_bucket()
    upload_xbrain_customer_interaction_in_bucket()
    upload_xbrain_conversation_log_in_bucket()
    upload_purchase_assistant_record_in_bucket()
    upload_item_purchased_in_bucket()
    upload_trade_area_analysis_in_bucket()
    upload_customer_location_behavior_in_bucket()
    upload_website_interaction_in_bucket()
    upload_customer_demographic_in_bucket()
    upload_technical_metadata_in_bucket()
    upload_loyalty_program_in_bucket()
    upload_marketing_preference_in_bucket()
    upload_note_and_activities_in_bucket()
    upload_lead_source_in_bucket()
    upload_social_media_profile_in_bucket()
    upload_purchase_history_in_bucket()
    upload_support_assistant_record_in_bucket()
