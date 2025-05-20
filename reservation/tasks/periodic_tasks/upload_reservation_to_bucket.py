import logging
from celery import shared_task
from examples.bucket_upload_helper import upload_data_in_bucket
from django.db import transaction
from reservation.models import (
    CommunicationLog,
    PreferenceAndRestriction,
    Guest,
    VisitHistory,
    MarketingData,
    Payment,
    Reservation,
    ModificationHistory,
    Restaurant,
    StaffAssignment,
    TechnicalMetadata,
    Waitlist,
)

logger = logging.getLogger(__name__)


def upload_communication_log_in_bucket(batch_size=1000):
    communication_logs = CommunicationLog.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in communication_logs:
        data = {
            "communication_log_id": item.pk,
            "guest_id": item.guest.pk,
            "reservation_id": item.reservation.pk if item.reservation else None,
            "communication_type": (
                item.communication_type if item.communication_type else None
            ),
            "method": item.method,
            "content": item.content,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "status": item.status,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="communication_log",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    CommunicationLog.objects.filter(
                        pk__in=successfully_uploaded
                    ).update(upload_bucket=True)
                successfully_uploaded = []
        except Exception as e:
            logger.error(
                f"Error uploading Communication Log (ID {item.pk}) to GCP: {e}"
            )

    CommunicationLog.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_preference_and_restriction_in_bucket(batch_size=1000):
    preferences = PreferenceAndRestriction.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in preferences:
        data = {
            "preference_and_restriction_id": item.pk,
            "guest_id": item.guest.pk,
            "preference_type": item.preference_type,
            "preference_detail": item.preference_detail,
            "notes": item.notes if item.notes else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="preference_and_restriction",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    PreferenceAndRestriction.objects.filter(
                        pk__in=successfully_uploaded
                    ).update(upload_bucket=True)
                successfully_uploaded = []

        except Exception as e:
            logger.error(
                f"Error uploading PreferenceAndRestriction (ID {item.pk}) to GCP: {e}"
            )

    PreferenceAndRestriction.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_guest_in_bucket(batch_size=1000):
    guests = Guest.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in guests:
        data = {
            "guest_id": item.pk,
            "first_name": item.first_name,
            "last_name": item.last_name,
            "email_address": item.email_address,
            "phone_number": item.phone_number,
            "loyalty_program_id": (
                item.loyalty_program_id if item.loyalty_program_id else None
            ),
            "vip_status": item.vip_status if item.vip_status else None,
            "guest_notes": item.guest_notes if item.guest_notes else None,
            "guest_tags": item.guest_tags if item.guest_tags else [],
            "birthdate": (
                item.birthdate.strftime("%Y-%m-%d") if item.birthdate else None
            ),
            "anniversary_date": (
                item.anniversary_date.strftime("%Y-%m-%d")
                if item.anniversary_date
                else None
            ),
            "gender": item.gender if item.gender else None,
            "nationality": item.nationality if item.nationality else None,
            "preferred_language": (
                item.preferred_language if item.preferred_language else None
            ),
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": item.updated_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "marketing_opt_in": (
                item.marketing_opt_in if item.marketing_opt_in else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="guest",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    Guest.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []
        except Exception as e:
            logger.error(f"Error uploading Guest (ID {item.pk}) to GCP: {e}")

    if successfully_uploaded:
        with transaction.atomic():
            Guest.objects.filter(pk__in=successfully_uploaded).update(
                upload_bucket=True
            )


def upload_visit_history_in_bucket(batch_size=1000):
    visit_histories = VisitHistory.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in visit_histories:
        data = {
            "visit_history_id": item.pk,
            "guest_id": item.guest.pk,
            "reservation_id": item.reservation.pk,
            "visit_date": item.visit_date.strftime("%Y-%m-%d"),
            "feedback": item.feedback if item.feedback else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="visit_history",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    VisitHistory.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []
        except Exception as e:
            logger.error(f"Error uploading VisitHistory (ID {item.pk}) to GCP: {e}")

    VisitHistory.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_marketing_data_in_bucket(batch_size=1000):
    marketing_data = MarketingData.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in marketing_data:
        data = {
            "marketing_data_id": item.pk,
            "reservation_id": item.reservation.pk,
            "campaign": item.campaign,
            "discount_code": item.discount_code if item.discount_code else None,
            "referral_source": item.referral_source,
            "survey_completed": item.survey_completed,
            "feedback_provided": (
                item.feedback_provided if item.feedback_provided else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="marketing_data",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    MarketingData.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []

        except Exception as e:
            logger.error(f"Error uploading MarketingData (ID {item.pk}) to GCP: {e}")

    MarketingData.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_payment_in_bucket(batch_size=1000):
    payments = Payment.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in payments:
        data = {
            "payment_id": item.pk,
            "reservation_id": item.reservation.pk,
            "payment_method": item.payment_method if item.payment_method else None,
            "payment_processor": (
                item.payment_processor if item.payment_processor else None
            ),
            "deposit_amount": (
                item.deposit_amount if item.deposit_amount is not None else None
            ),
            "deposit_refund_status": (
                item.deposit_refund_status if item.deposit_refund_status else None
            ),
            "total_spend": item.total_spend if item.total_spend is not None else None,
            "bill_split_details": (
                item.bill_split_details if item.bill_split_details else None
            ),
            "transaction_created_at": item.transaction_created_at.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="payment",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    Payment.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []

        except Exception as e:
            logger.error(f"Error uploading Payment (ID {item.pk}) to GCP: {e}")

    Payment.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_reservation_in_bucket(batch_size=1000):
    reservations = Reservation.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in reservations:
        data = {
            "reservation_id": item.pk,
            "reservation_source": item.reservation_source,
            "restaurant_id": item.restaurant.pk,
            "reservation_date": (
                item.reservation_date.strftime("%Y-%m-%d")
                if item.reservation_date
                else None
            ),
            "reservation_time": item.reservation_time.strftime("%H:%M:%S.%f"),
            "booking_datetime": item.booking_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "reservation_status": item.reservation_status,
            "number_of_guests": item.number_of_guests,
            "table_number": item.table_number if item.table_number else None,
            "special_requests": (
                item.special_requests if item.special_requests else None
            ),
            "reservation_channel": (
                item.reservation_channel if item.reservation_channel else None
            ),
            "cancellation_datetime": (
                item.cancellation_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
                if item.cancellation_datetime
                else None
            ),
            "check_in_status": item.check_in_status,
            "check_in_time": (
                item.check_in_time.strftime("%Y-%m-%d %H:%M:%S.%f")
                if item.check_in_time
                else None
            ),
            "waitlist_position": (
                item.waitlist_position if item.waitlist_position else None
            ),
            "confirmation_method": (
                item.confirmation_method if item.confirmation_method else None
            ),
            "booking_notes": item.booking_notes if item.booking_notes else None,
            "guest_id": item.guest.pk,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="reservation",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    Reservation.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []

        except Exception as e:
            logger.error(f"Error uploading Reservation (ID {item.pk}) to GCP: {e}")

    Reservation.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_modification_history_in_bucket(batch_size=1000):
    modification_histories = ModificationHistory.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in modification_histories:
        data = {
            "modification_history_id": item.pk,
            "reservation_id": item.reservation.pk,
            "modification": item.modification.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "modified_by": item.modified_by,
            "modification_notes": (
                item.modification_notes if item.modification_notes else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="modification_history",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    ModificationHistory.objects.filter(
                        pk__in=successfully_uploaded
                    ).update(upload_bucket=True)
                successfully_uploaded = []

        except Exception as e:
            logger.error(
                f"Error uploading ModificationHistory (ID {item.pk}) to GCP: {e}"
            )

    ModificationHistory.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_restaurant_in_bucket(batch_size=1000):
    restaurants = Restaurant.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in restaurants:
        data = {
            "restaurant_id": item.pk,
            "restaurant_name": item.restaurant_name,
            "venue_address": item.venue_address,
            "venue_capacity": item.venue_capacity if item.venue_capacity else None,
            "table_layout": item.table_layout if item.table_layout else None,
            "operational_notes": (
                item.operational_notes if item.operational_notes else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="restaurant",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    Restaurant.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []

        except Exception as e:
            logger.error(f"Error uploading Restaurant (ID {item.pk}) to GCP: {e}")

    Restaurant.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


def upload_staff_assignment_in_bucket(batch_size=1000):
    staff_assignments = StaffAssignment.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in staff_assignments:
        data = {
            "staff_assignment_id": item.pk,
            "reservation_id": item.reservation.pk,
            "staff_member_id": item.staff_member_id if item.staff_member_id else None,
            "staff_member_name": item.staff_member_name,
            "role": item.role if item.role else None,
            "notes_for_staff": item.notes_for_staff if item.notes_for_staff else None,
            "turnover_time": item.turnover_time if item.turnover_time else None,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="staff_assignment",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    StaffAssignment.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []

        except Exception as e:
            logger.error(f"Error uploading StaffAssignment (ID {item.pk}) to GCP: {e}")

    StaffAssignment.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_technical_metadata_in_bucket(batch_size=1000):
    technical_metadata = TechnicalMetadata.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in technical_metadata:
        data = {
            "technical_metadata_id": item.pk,
            "reservation_id": item.reservation.pk,
            "api_call": item.api_call if item.api_call else None,
            "data_source": item.data_source,
            "data_sync_status": (
                item.data_sync_status if item.data_sync_status else None
            ),
            "data_retrieval_created_at": item.data_retrieval_created_at.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
            "processing_notes": (
                item.processing_notes if item.processing_notes else None
            ),
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="technical_metadata",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    TechnicalMetadata.objects.filter(
                        pk__in=successfully_uploaded
                    ).update(upload_bucket=True)
                successfully_uploaded = []

        except Exception as e:
            logger.error(
                f"Error uploading TechnicalMetadata (ID {item.pk}) to GCP: {e}"
            )

    TechnicalMetadata.objects.filter(pk__in=successfully_uploaded).update(
        upload_bucket=True
    )


def upload_waitlist_in_bucket(batch_size=1000):
    waitlists = Waitlist.objects.filter(upload_bucket=False)
    successfully_uploaded = []

    for item in waitlists:
        data = {
            "waitlist_id": item.pk,
            "guest_id": item.guest.pk,
            "restaurant_id": item.restaurant.pk,
            "position": item.position,
            "added_datetime": item.added_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "estimated_wait_time": item.estimated_wait_time,
            "status": item.status,
        }

        try:
            upload_data_in_bucket(
                item_pk=item.pk,
                data=data,
                app_name="reservation",
                model_name="waitlist",
            )
            successfully_uploaded.append(item.pk)
            if len(successfully_uploaded) >= batch_size:
                with transaction.atomic():
                    Waitlist.objects.filter(pk__in=successfully_uploaded).update(
                        upload_bucket=True
                    )
                successfully_uploaded = []

        except Exception as e:
            logger.error(f"Error uploading Waitlist (ID {item.pk}) to GCP: {e}")

    Waitlist.objects.filter(pk__in=successfully_uploaded).update(upload_bucket=True)


@shared_task
def upload_reservation_data_to_bucket():

    upload_guest_in_bucket()
    upload_visit_history_in_bucket()
    upload_marketing_data_in_bucket()
    upload_payment_in_bucket()
    upload_reservation_in_bucket()
    upload_modification_history_in_bucket()
    upload_restaurant_in_bucket()
    upload_staff_assignment_in_bucket()
    upload_technical_metadata_in_bucket()
    upload_waitlist_in_bucket()
    upload_communication_log_in_bucket()
    upload_preference_and_restriction_in_bucket()
