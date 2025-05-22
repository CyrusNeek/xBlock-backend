from celery import shared_task
import pytz
from report.model_fields import REPORT_USER_FIELDS, TOCK_BOOKING_FIELDS
from report.models.report_user import ReportUser
from report.models.tock_booking import TockBooking
from web.models.unit import Unit
from web.services.weaviate import WeaviateManager
from web.services.weaviate import WeaviateManager
from weaviate.classes.config import Property, DataType, ReferenceProperty, Configure
from django.utils import timezone


def insert_tock_bookings_to_weaviate(manager: WeaviateManager, unit: int):
    brand_timezone = Unit.objects.get(pk=unit).brand.owner.timezone

    today = timezone.now().date()
    tock_bookings = TockBooking.objects.filter(
        tock__unit__pk=unit, time__date=today
    )

    if not tock_bookings.exists():
        print("No Tock Bookings found for the specified unit.")
        return
    collection_name = "tockBookings"
    data = []
    for booking in tock_bookings.values(*TOCK_BOOKING_FIELDS):
        data_obj = {
            "id_tock_booking": booking["pk"],
            "time": (
                booking["time"].astimezone(pytz.timezone(brand_timezone)).isoformat()
                if booking["time"]
                else None
            ),
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
            "user": (
                manager.get_object("userProfile", user_id=booking["user"])
                if booking["user"]
                else None
            ),
            "ai_description": None,
            "timezone": brand_timezone,
        }

        data.append(data_obj)

    manager.create_bulk(collection_name, data)
    tock_bookings.update(uploaded=True)


def insert_users_to_weaviate(manager: WeaviateManager, unit: int):
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
        num -= 1

    manager.create_bulk(collection_name, data)
    users.update(uploaded=True)

def empty_tock_bookings_collection():
    manager = WeaviateManager()
    manager.empty_collection(
        name="tockBookings",
        fields=[
            Property(name="unit", data_type=DataType.INT),
            Property(name="block_category", data_type=DataType.INT),
            Property(name="id_tock_booking", data_type=DataType.NUMBER),
            Property(name="time", data_type=DataType.DATE),
            Property(name="status", data_type=DataType.TEXT),
            Property(name="tags", data_type=DataType.TEXT),
            Property(name="postal_code", data_type=DataType.TEXT),
            Property(name="party_size", data_type=DataType.TEXT),
            Property(name="booking_owner", data_type=DataType.TEXT),
            Property(name="experience", data_type=DataType.TEXT),
            Property(name="price_per_person", data_type=DataType.NUMBER),
            Property(name="supplements", data_type=DataType.TEXT),
            Property(name="question_answers", data_type=DataType.TEXT),
            Property(name="visit_notes", data_type=DataType.TEXT),
            Property(name="visit_dietary_notes", data_type=DataType.TEXT),
            Property(name="guest_providede_order_notes", data_type=DataType.TEXT),
            Property(name="guest_notes", data_type=DataType.TEXT),
            Property(name="dietary_notes", data_type=DataType.TEXT),
            Property(name="total_price", data_type=DataType.NUMBER),
            Property(name="gross_amount_paid", data_type=DataType.NUMBER),
            Property(name="net_amount_paid", data_type=DataType.NUMBER),
            Property(name="service_charge", data_type=DataType.NUMBER),
            Property(name="gratuity", data_type=DataType.NUMBER),
            Property(name="visits", data_type=DataType.INT),
            Property(name="tables", data_type=DataType.TEXT),
            Property(name="servers", data_type=DataType.TEXT),
            Property(name="booking_method", data_type=DataType.TEXT),
            Property(name="spouse_name", data_type=DataType.TEXT),
            Property(name="ai_description", data_type=DataType.TEXT),
            Property(name="timezone", data_type=DataType.TEXT),
        ],
        references=[ReferenceProperty(name="user", target_collection="userProfile")],
        vectorizer_config=[
            Configure.NamedVectors.text2vec_openai(
                name="embed_time",
                source_properties=["time"],
            )
        ],
    )

@shared_task
def run_all_weaviate_tasks():
    manager = WeaviateManager()

    empty_tock_bookings_collection()
    insert_users_to_weaviate(manager, 9)
    insert_tock_bookings_to_weaviate(manager, 9)
