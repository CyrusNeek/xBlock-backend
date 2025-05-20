import datetime
from celery import shared_task
import logging
from django.db.models import Q
from report.models.guest_profile import Guest, GuestProfile
from report.models.resy_reservation import ResyReservation
from report.models.tock_booking import TockBooking
from report.tasks.periodic.guest_match import guest_match_data


logger = logging.getLogger(__name__)


def reset():
    ResyReservation.objects.all().update(is_new=True)
    TockBooking.objects.all().update(is_new=True)
    GuestProfile.objects.all().delete()
    Guest.objects.all().delete()


def create_profile():
    # first read data from Resy and Tock
    # Resy
    resy_data = ResyReservation.objects.filter(is_new=True)
    logger.info(f"start Resy matching {resy_data.count()} guests")
    # use Model Guest to create object
    for item in resy_data:
        filters = Q(phone=item.phone) & Q(brand=item.brand)
        if item.email:
            filters |= Q(email=item.email)
        guest = Guest.objects.filter(filters)
        if not guest.exists():
            logger.info(f"create new guest {item.first_name} {item.last_name}")
            guest = Guest.objects.create(
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                phone=item.phone,
                brand=item.brand,
            )
        else:
            logger.info(f"found guest {item.first_name} {item.last_name}")
            guest = guest.first()
        # create guest profie use method create or update
        guest_profile, created = GuestProfile.objects.update_or_create(
            model_name="Resy",
            object_id=item.pk,
            defaults={
                "total_price": 0.0,
                "user": guest,
                "reservation_date": item.datetime,
                "tables": item.table
            }
        )
        item.is_new = False
        item.save()

    tock_data = TockBooking.objects.filter(is_new=True)
    logger.info(f"start Tock matching {tock_data.count()} guests")
    for item in tock_data:
        filters = Q(phone=item.phone) & Q(brand=item.brand)
        if item.email:
            filters |= Q(email=item.email)
        guest = Guest.objects.filter(filters)
        if not guest.exists():
            guest = Guest.objects.create(
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                phone=item.phone,
                brand=item.brand,
            )
        else:
            guest = guest.first()
        # create guest profie use method create or update
        guest_profile, created = GuestProfile.objects.update_or_create(
            model_name="Tock",
            object_id=item.pk,
            defaults={
                "total_price": 0.0,
                "user": guest,
                "reservation_date": item.time,
                "tables": item.tables
            }
        )
        item.is_new = False
        item.save()


def fix_guest_match():
    today = datetime.date.today()
    data = GuestProfile.objects.filter(matched=GuestProfile.M_NEW)
    logger.info(f"INFO: start fix data match {data.count()} guests")
    for item in data:
        obj = None
        if item.model_name == "Resy":
            obj = ResyReservation.objects.get(pk=item.object_id)
        elif item.model_name == "Tock":
            obj = TockBooking.objects.get(pk=item.object_id)
        if not obj:
            print(
                f"Object not found for {item.model_name} with id {item.object_id}")
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
            item.matched = GuestProfile.M_INITIAL_MATCHED
            item.save()
            print(
                f"Guest created for {obj.first_name} {obj.last_name} phone: {obj.phone} email{obj.email}")
        else:
            print(f"count user found: {guest.count()}")
            guest_pk = guest.first()
            if guest_pk.pk == item.user.pk:
                item.matched = GuestProfile.M_INITIAL_MATCHED
                item.save()
                print(
                    f"User {obj.first_name} {obj.last_name} phone: {guest_pk.phone} email{guest_pk.email} is correct")
            else:
                print("-"*10)
                print(
                    f"User {obj.first_name} {obj.last_name} phone: {guest_pk.phone} email{guest_pk.email} is not correct {obj.pk} gu:{guest_pk.pk}")
                print("-"*10)
                item.user = guest_pk
                item.matched = GuestProfile.M_INITIAL_MATCHED
                item.save()


@shared_task
def combine_tock_and_resy():
    logger.info(f"INFO: Start Create Profile from Resy and Tock")
    create_profile()
    logger.info("INFO: Start Fix match data")
    fix_guest_match()
    logger.info(f"INFO: Start Match Data Sql")
    guest_match_data.delay()


@shared_task()
def lifetime_calculate():
    guest = Guest.objects.prefetch_related('profiles').filter(profiles__toast__isnull=False).all()
    print(f"Start calculate lifetime and total visits for {guest.count()} guests")
    # sum field amount inside model ToastOrder and count total visits
    # each guest profile has a ToastOrder (related toast field)
    for item in guest:
        total_lifetime = 0
        total_visits = 0
        for profile in item.profiles.all():
            if profile.toast:
                total_lifetime += profile.toast.total
                total_visits += 1
        item.Lifetime_value = total_lifetime
        item.total_visits = total_visits
        item.save()

