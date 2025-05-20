import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xblock.settings")


django.setup()


from report.models import ToastOrder, TockBooking, ResyReservation, ReportUser
from report.model_fields import (
    REPORT_USER_FIELDS,
    RESY_RESERVATION_FIELDS,
    TOAST_ORDER_FIELDS,
    TOCK_BOOKING_FIELDS,
)
from web.models import Unit, UnitFile
from web.models.unit_file_fields import UNIT_FILE_FIELDS
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta, datetime

from web.services.weaviate import WeaviateManager
from weaviate.classes.config import Property, DataType, ReferenceProperty
from examples.weaviate.insert_description_data import generate_description_from_json
from web.models import Brand, BrandOwner

import pytz


def insert_users_to_weaviate(manager: WeaviateManager, unit: Unit):
    users = ReportUser.objects.filter(brand__units__in=[unit], uploaded=False)
    num = ReportUser.objects.filter(brand__units__in=[unit], uploaded=False).count()

    collection_name = "userProfile"

    if not users.exists():
        return

    data = []
    for user in users.values(*REPORT_USER_FIELDS):
        data_obj = {
            "user_id": user["pk"],
            "email": user["email"],
            "phone": user["phone"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "brand": user["brand"],
        }

        data.append(data_obj)
        print(f"objects remaining {num}")
        num -= 1

    manager.create_bulk(collection_name, data)
    users.update(uploaded=True)


def insert_orders_to_weaviate(manager: WeaviateManager, unit: Unit):
    one_month_ago = timezone.now() - timedelta(days=7)
    orders = ToastOrder.objects.filter(
        toast_auth__unit=unit, uploaded=False, opened__gte=one_month_ago
    )

    if not orders.exists():
        print("No orders found for the specified unit.")
        return

    collection_name = "orders"

    data = []
    for order in orders.values(*TOAST_ORDER_FIELDS):
        data_obj = {
            "order_id": order["pk"],
            "block_category": order["toast_auth__block_category__pk"],
            "unit": order["toast_auth__unit__pk"],
            "order_number": order["order_number"],
            "checks": order["checks"],
            "opened": order["opened"].isoformat() if order["opened"] else None,
            "number_of_guests": order["number_of_guests"],
            "tab_names": order["tab_names"],
            "table": order["table"],
            "amount": float(order["amount"]),
            "discount_amount": float(order["discount_amount"]),
            "service": order["service"],
            "tax": float(order["tax"]),
            "tip": float(order["tip"]),
            "gratuity": float(order["gratuity"] or 0.00),
            "total": float(order["total"]),
            # "user": manager.get_object("userProfile", user_id=order['user']) if order['user'] else None
        }

        description = generate_description_from_json(data_obj)
        data_obj["ai_description"] = description

        data.append(data_obj)

    manager.create_bulk(collection_name, data)
    orders.update(uploaded=True)


def insert_resy_reservations_to_weaviate(manager: WeaviateManager, unit: Unit):
    one_month_ago = timezone.now() - timedelta(days=7)
    reservations = ResyReservation.objects.filter(
        resy_auth__unit=unit, uploaded=False, created_at__gte=one_month_ago
    )

    if not reservations.exists():
        print("No reservations found for the specified unit.")
        return

    collection_name = "resyReservations"

    data = []
    for reservation in reservations.values(*RESY_RESERVATION_FIELDS):
        data_obj = {
            "time": reservation["time"],
            "datetime": (
                reservation["datetime"].isoformat() if reservation["datetime"] else None
            ),
            "block_category": reservation["resy_auth__block_category__pk"],
            "unit": reservation["resy_auth__unit__pk"],
            "service": reservation["service"],
            "guest": reservation["guest"],
            "phone": reservation["phone"],
            "email": reservation["email"],
            "party_size": str(reservation["party_size"] or 0),
            "status": reservation["status"],
            "table": reservation["table"],
            "visit_note": reservation["visit_note"],
            "reserve_number": reservation["reserve_number"],
            # "user": manager.get_object("userProfile", user_id=reservation['user'])
        }

        description = generate_description_from_json(data_obj)
        data_obj["ai_description"] = description

        data.append(data_obj)

    manager.create_bulk(collection_name, data)
    reservations.update(uploaded=True)


def insert_tock_bookings_to_weaviate(manager: WeaviateManager, unit: Unit):
    brand_timezone = Unit.objects.get(pk=unit).brand.owner.timezone  
    
    today = datetime.now().date()
    tock_bookings = TockBooking.objects.filter(
        tock__unit__pk=unit,
        # uploaded=False,
        time__date=today,
        # status__in=[TockBooking.BookStatus.BOOKED, TockBooking.BookStatus.CANCELED]
    )

    if not tock_bookings.exists():
        print("No Tock Bookings found for the specified unit.")
        return
    collection_name = "tockBookings"
    data = []
    for booking in tock_bookings.values(*TOCK_BOOKING_FIELDS):
        data_obj = {
            "id_tock_booking" : booking["pk"],
            "time": booking["time"].astimezone(pytz.timezone(brand_timezone)).isoformat() if booking["time"] else None,
            "status": booking["status"],
            "postal_code": booking["postal_code"],
            "party_size": str(booking["party_size"]),
            "booking_owner": booking["booking_owner"],
            "experience": booking["experience"],
            "price_per_person": float(booking["price_per_person"]),
            "supplements": booking["supplements"],
            "question_answers": booking["question_answers"],
            "visit_notes": booking["visit_notes"],
            "visit_dietary_notes": booking["visit_dietary_notes"],
            "guest_provided_order_notes": booking["guest_provided_order_notes"],
            "guest_notes": booking["guest_notes"],
            "dietary_notes": booking["dietary_notes"],
            "total_price": float(booking["total_price"]),
            "gross_amount_paid": float(booking["gross_amount_paid"]),
            "net_amount_paid": float(booking["net_amount_paid"]),
            "service_charge": float(booking["service_charge"] or 0.00),
            "gratuity": float(booking["gratuity"] or 0.00),
            "visits": booking["visits"],
            "tables": booking["tables"],
            "servers": booking["servers"],
            "booking_method": booking["booking_method"],
            "spouse_name": booking["spouse_name"],
            "unit": unit,
            "block_category": booking["tock__block_category__pk"],
            "user": manager.get_object("userProfile", user_id=booking["user"]) if booking["user"] else None,
            "ai_description" : None,
            "timezone": brand_timezone,
        }

        data.append(data_obj)

    manager.create_bulk(collection_name, data)
    tock_bookings.update(uploaded=True)


# def insert_unit_files_to_weaviate(manager: WeaviateManager, unit: Unit):
#     unit_files = UnitFile.objects.filter(user__unit__pk=unit.pk, uploaded=False)

#     if not unit_files.exists():
#         print("No unit files found for the specified user.")
#         return

#     collection_name = "unitFiles"

#     data = []
#     for file in unit_files.values(*UNIT_FILE_FIELDS):
#         data.append({
#             "unit_id": file["user__unit__pk"],
#             "file_url": file["file_url"],
#             "file_description": file["file_description"],
#             "created_at": file["created_at"],
#             "updated_at": file["updated_at"],
#             "file_name": file["file_name"],
#             "uploaded": file["uploaded"],
#             "file_size": file["file_size"],
#             "file_type": file["file_type"],
#             "openai_file_id": file["openai_file_id"],
#             # "user": manager.get_object("users", user_id=file.user.id) if file.user else None,
#         })

#     manager.create_bulk(collection_name, data)


def main():
    units = Unit.objects.filter(brand__pk=7)
    manager = WeaviateManager()
    # for unit in units:
    insert_users_to_weaviate(manager, 9)
        # insert_orders_to_weaviate(manager, unit)
    insert_tock_bookings_to_weaviate(manager, 9)
        # insert_resy_reservations_to_weaviate(manager, unit)
        # insert_unit_files_to_weaviate(manager, unit)


if __name__ == "django.core.management.commands.shell":
    main()
