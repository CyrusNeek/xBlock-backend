
from django.core.management.base import BaseCommand

from report.models.guest_profile import Guest, GuestProfile
from report.models.resy_reservation import ResyReservation

import logging

from report.models.tock_booking import TockBooking
from report.tasks.periodic.guest_match import guest_match_data
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = GuestProfile.objects.all()
        for item in data:
            obj = None
            if item.model_name == "Resy":
                obj = ResyReservation.objects.get(pk=item.object_id)
            elif item.model_name == "Tock":
                obj = TockBooking.objects.get(pk=item.object_id)
            if not obj:
                print(f"Object not found for {item.model_name} with id {item.object_id}")
            # check object that is correct user (check firstname,lastname and (phone or email)
            filters = {
                "brand": obj.brand,
            }
            if obj.email:
                filters["email"] = obj.email
            if obj.phone and obj.phone != "-":
                filters["phone"] = obj.phone
            if obj.first_name:
                filters["first_name"] = obj.first_name
            if obj.last_name:
                filters["last_name"] = obj.last_name
            guest = Guest.objects.filter(**filters)
            if not guest.exists():
                print(f"Guest Not found filter:{filters}")
                 # create Guest
                guest = Guest.objects.create(
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    email=obj.email,
                    phone=obj.phone,
                    brand=obj.brand,
                )
                item.user = guest
                item.save()
                print(f"Guest created for {obj.first_name} {obj.last_name} phone: {obj.phone} email{obj.email}")
            else:
                print(f"count user found: {guest.count()}")
                guest_pk = guest.first()
                if guest_pk.pk == item.user.pk:
                    print(f"User {obj.first_name} {obj.last_name} phone: {guest_pk.phone} email{guest_pk.email} is correct")
                else:
                    print("-"*10)
                    print(f"User {obj.first_name} {obj.last_name} phone: {guest_pk.phone} email{guest_pk.email} is not correct {obj.pk} gu:{guest_pk.pk}")
                    print("-"*10)
                    item.user = guest_pk
                    item.save()

