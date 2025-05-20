from celery import shared_task
import logging
from report.models import (
    ResyReservation,
    GuestProfile,
    TockBooking,
    ToastOrder,
    ToastItemSelectionDetails,
    ToastCashTransaction,
)
from report.models import Guest as ReportGuest
from report.tasks.periodic.guest_match import merge_resy_date_time
from web.models import Unit
from pos.models import Payment as POSPayment
from pos.models import (
    Transaction,
    TransactionItem,
    Customer,
    RestaurantLocation,
    Staff,
    DiscountPromotion,
    ShiftDetail,
)
from reservation.models import (
    Reservation,
    Guest,
    Restaurant,
    Payment,
    StaffAssignment,
    TechnicalMetadata,
    PreferenceAndRestriction,
    VisitHistory,
    Waitlist,
    CommunicationLog,
)

logger = logging.getLogger(__name__)


def create_reservation_objects():
    guests = GuestProfile.objects.filter(new_models=False)

    for item in guests:
        try:
            # Retrieve old model guest
            guest = ReportGuest.objects.get(pk=item.user.pk)

            # Get or create new model guest
            new_guest, _ = Guest.objects.get_or_create(
                first_name=guest.first_name or None,
                last_name=guest.last_name or None,
                email_address=guest.email or None,
                phone_number=guest.phone or None,
                created_at=guest.created_at,
                updated_at=guest.updated_at,
            )

            if item.model_name == "Resy":
                create_resy_reservation(item, new_guest)

            elif item.model_name == "Tock":
                create_tock_reservation(item, new_guest)

            if item.toast:
                create_toast_transaction(item, guest, new_guest)

        except ReportGuest.DoesNotExist:
            logger.warning(f"Guest with ID {item.user.pk} does not exist.")
        except Exception as e:
            logger.warning(f"An error occurred: {str(e)}")


def create_resy_reservation(item, new_guest):
    try:
        resy = ResyReservation.objects.get(pk=item.object_id)
        unit = Unit.objects.get(pk=resy.resy_auth.unit.pk)

        # Create restaurant and reservation records
        resturant, _ = Restaurant.objects.get_or_create(
            restaurant_name=unit.name,
            venue_address=unit.address or None,
        )

        reservation_datetime = merge_resy_date_time(resy.reservation_date, resy.time)

        reservation, _ = Reservation.objects.update_or_create(
            reservation_source=item.model_name,
            restaurant=resturant,
            reservation_date=reservation_datetime.date(),
            reservation_time=reservation_datetime.time(),
            booking_datetime=resy.created_at,
            reservation_status=resy.status,
            number_of_guests=resy.party_size or None,
            table_number=resy.table or None,
            special_requests=resy.special_requests or None,
            check_in_status=True if item.toast else False,
            guest=new_guest,
        )

        TechnicalMetadata.objects.get_or_create(
            reservation=reservation,
            data_source="Resy Reservation",
            data_retrieval_created_at=resy.created_at,
        )

        VisitHistory.objects.get_or_create(
            guest=new_guest,
            reservation=reservation,
            visit_date=resy.created_at.date(),
        )

    except Exception as e:
        logger.warning(f"Error processing Resy reservation: {str(e)}")


def create_tock_reservation(item, new_guest):
    try:
        tock = TockBooking.objects.get(pk=item.object_id)
        if tock.birthday:
            new_guest.birthdate = tock.birthday
            new_guest.save(update_fields=["birthdate"])

        unit = Unit.objects.get(pk=tock.tock.unit.pk)

        # Create restaurant and reservation records
        resturant, _ = Restaurant.objects.get_or_create(
            restaurant_name=unit.name,
            venue_address=unit.address or None,
        )

        reservation, _ = Reservation.objects.update_or_create(
            reservation_source=item.model_name,
            restaurant=resturant,
            reservation_date=tock.time.date() or None,
            reservation_time=tock.time.time() or None,
            booking_datetime=tock.report_triggered_at,
            reservation_status=tock.final_status or None,
            number_of_guests=tock.party_size,
            table_number=tock.tables or None,
            special_requests=tock.guest_notes or None,
            check_in_status=True if item.toast else False,
            confirmation_method=tock.booking_method or None,
            guest=new_guest,
        )

        # Handle staff assignments
        if tock.servers:
            servers = [server.strip() for server in tock.servers.split(",")]
            for server in servers:
                StaffAssignment.objects.get_or_create(
                    reservation=reservation, staff_member_name=server
                )

        # Create payment and technical metadata records
        Payment.objects.get_or_create(
            reservation=reservation,
            deposit_amount=tock.gross_amount_paid or None,
            total_spend=tock.total_price or None,
            bill_split_details=(
                f"Price per person: {tock.price_per_person}"
                if tock.price_per_person
                else None
            ),
        )

        TechnicalMetadata.objects.get_or_create(
            reservation=reservation,
            data_source="Tock booking service",
            data_retrieval_created_at=tock.report_triggered_at,
        )

        # Save preferences
        preference_data = {
            "guest notes": tock.guest_notes or None,
            "visit notes": tock.visit_notes or None,
            "dietary notes": tock.dietary_notes or None,
            "visit dietary notes": tock.visit_dietary_notes or None,
            "guest provided order notes": tock.guest_provided_order_notes or None,
        }
        for preference_type, preference_detail in preference_data.items():
            PreferenceAndRestriction.objects.get_or_create(
                guest=new_guest,
                preference_type=preference_type,
                preference_detail=preference_detail,
            )

        VisitHistory.objects.get_or_create(
            guest=new_guest,
            reservation=reservation,
            visit_date=tock.report_triggered_at.date(),
        )

    except Exception as e:
        logger.warning(f"Error processing Tock reservation: {str(e)}")


def create_toast_transaction(item, guest, new_guest):
    try:
        toast = ToastOrder.objects.get(pk=item.object_id)
        if not toast.is_valid:
            return

        unit = Unit.objects.get(pk=toast.unit.pk)
        resturant, _ = RestaurantLocation.objects.get_or_create(
            restaurant_name=unit.name,
            address=unit.address or None,
            city=unit.city or None,
            state=unit.state or None,
            zip_code=unit.zip_code or None,
            phone_number=unit.phone_number or None,
            email=unit.email or None,
        )

        # Create customer and transaction records
        customer = Customer.objects.create(
            first_name=toast.user.first_name,
            last_name=toast.user.last_name,
            email=toast.user.email or None,
            phone_number=toast.user.phone or None,
            birthdate=new_guest.birthdate or None,
            total_visits=guest.total_visits,
            total_spend=guest.Lifetime_value,
            last_visit_date=guest.updated_at,
        )

        transaction_status = (
            Transaction.VOIDED if toast.voided else Transaction.COMPLETED
        )
        transaction = Transaction.objects.create(
            pos_system="Toast",
            restaurant_location=resturant,
            transaction_date=toast.opened.date(),
            transaction_time=toast.opened.time(),
            order_type=toast.order_source,
            order_status=transaction_status,
            subtotal_amount=toast.amount,
            tax_amount=toast.tax,
            tip_amount=toast.tip,
            total_amount=toast.total,
            discount_amount=toast.discount_amount,
            customer=customer,
            table_number=toast.table or None,
            transaction_datetime=toast.paid or None,
        )

        toast_item = ToastItemSelectionDetails.objects.get(order=toast)
        TransactionItem.objects.create(
            transaction=transaction,
            item_name=toast_item.menu_item or None,
            item_sku=toast_item.sku or None,
            item_category=toast_item.sales_category or None,
            quantity=int(toast_item.quantity),
            unit_price=toast_item.gross_price,
            modifier_details=f"menu group: {toast_item.menu_group}, menu: {toast_item.menu}",
            discount_applied=toast_item.discount,
            total_item_price=toast_item.net_price,
        )

    except Exception as e:
        logger.warning(f"Error processing Toast transaction: {str(e)}")


@shared_task
def create_report_app_new_models_object():
    create_reservation_objects()
