
from django.core.management.base import BaseCommand

from report.models.guest_profile import Guest, GuestProfile
from report.models.resy_reservation import ResyReservation

import logging

from report.models.tock_booking import TockBooking
from report.tasks.periodic.guest_match import guest_match_data
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = GuestProfile.objects.filter(reservation_date__isnull=True)
        print("INFO: start count data:", data.count())
        cn = 0
        for item in data:
            obj = None
            if item.model_name == "Resy":
                obj = ResyReservation.objects.get(pk=item.object_id)
            elif item.model_name == "Tock":
                obj = TockBooking.objects.get(pk=item.object_id)
            if not obj:
                print(f"Object not found for {item.model_name} with id {item.object_id}")
            reservation_date = None
            if item.model_name == GuestProfile.RESY:
                reservation_date = obj.datetime
            elif item.model_name == GuestProfile.TOCK:
                reservation_date = obj.time
            item.reservation_date = reservation_date
            item.save()
            cn +=1
            print(f"INFO: Reservation date updated for {item.model_name} with id {item.object_id} to {reservation_date}")
        print("INFO: End count data:", cn, "from total:", data.count())

