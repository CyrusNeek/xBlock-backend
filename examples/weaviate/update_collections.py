import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xblock.settings")


django.setup()


from web.services.weaviate import WeaviateManager
from report.models import TockBooking
from datetime import datetime
from report.model_fields import TOCK_BOOKING_FIELDS
from web.models import Unit
import pytz


def update_tock_booking_collection(manager: WeaviateManager, unit):
    brand_timezone = Unit.objects.get(pk=unit.pk).brand.owner.timezone
    today = datetime.now().date()
    tock_bookings = TockBooking.objects.filter(tock__unit__pk=unit.pk, uploaded=True, time__date=today)
    count = TockBooking.objects.filter(tock__unit__pk=unit.pk, uploaded=True, time__date=today).count()

    if not tock_bookings.exists():
        print("No Tock Bookings found for the specified unit.")
        return
    
    collection = manager.get_collection("tockBookings")
    
    for obj in collection.iterator():
        tock_obj = TockBooking.objects.filter(pk=int(obj.properties.get("id_tock_booking")))
        uuid = str(obj.uuid)
        updated_obj = {
            "id_tock_booking" : tock_obj["pk"],
            "time": tock_obj["time"].astimezone(pytz.timezone(brand_timezone)).isoformat() if tock_obj["time"] else None,
            "status": tock_obj["status"],
            "postal_code": tock_obj["postal_code"],
            "party_size": str(tock_obj["party_size"]),
            "booking_owner": tock_obj["booking_owner"],
            "experience": tock_obj["experience"],
            "price_per_person": float(tock_obj["price_per_person"]),
            "supplements": tock_obj["supplements"],
            "question_answers": tock_obj["question_answers"],
            "visit_notes": tock_obj["visit_notes"],
            "visit_dietary_notes": tock_obj["visit_dietary_notes"],
            "guest_provided_order_notes": tock_obj["guest_provided_order_notes"],
            "guest_notes": tock_obj["guest_notes"],
            "dietary_notes": tock_obj["dietary_notes"],
            "total_price": float(tock_obj["total_price"]),
            "gross_amount_paid": float(tock_obj["gross_amount_paid"]),
            "net_amount_paid": float(tock_obj["net_amount_paid"]),
            "service_charge": float(tock_obj["service_charge"] or 0.00),
            "gratuity": float(tock_obj["gratuity"] or 0.00),
            "visits": tock_obj["visits"],
            "tables": tock_obj["tables"],
            "servers": tock_obj["servers"],
            "booking_method": tock_obj["booking_method"],
            "spouse_name": tock_obj["spouse_name"],
            "unit": unit.pk,
            "block_category": tock_obj["tock__block_category__pk"],
            "user": manager.get_object("userProfile", user_id=tock_obj["user"]),
            "ai_description" : None,
            "timezone": brand_timezone,
        }
        
        
        
        collection.data.replace(
            uuid=uuid,
            properties=updated_obj
        )
        count-=1
        print(count)

def main():
    manager = WeaviateManager()
    update_tock_booking_collection(manager, unit=9)
    
    
if __name__ == "django.core.management.commands.shell":
    main()