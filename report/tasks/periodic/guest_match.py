from celery import shared_task
import logging
from django.db.models import Q
from report.models.guest_profile import Guest, GuestProfile
from report.models.resy_reservation import ResyReservation
from report.models.toast_order import ToastOrder
from report.models.tock_booking import TockBooking
from django.utils.timezone import timedelta
from datetime import datetime
import pytz
from django.utils.timezone import make_aware

from web.models import toast
from xblock.settings import TIME_ZONE


logger = logging.getLogger(__name__)


def merge_resy_date_time(reservation_date: str, time: str) -> datetime:
    """
    Merge the reservation_date and time from Resy into a datetime object.
    Returns a timezone-aware datetime object or None if parsing fails.
    """
    if not reservation_date or not time:
        return None

    try:
        # Attempt to parse reservation_date as ISO 8601 format
        dt = datetime.fromisoformat(reservation_date)
    except ValueError:
        try:
            # If ISO parsing fails, try the custom format: "Friday October 13, 2023"
            dt = datetime.strptime(reservation_date, "%A %B %d, %Y")
        except ValueError as e:
            logger.error(
                f"Failed to parse reservation date: {reservation_date}, Error: {e}")
            return None

    # Combine the parsed date with the time
    datetime_str = f"{dt.strftime('%Y-%m-%d')} {time}"

    try:
        # Attempt to parse time as 24-hour format (e.g., '18:00:00')
        final_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # If the first attempt fails, try 12-hour format (e.g., '6:00 PM')
            final_dt = datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
        except ValueError as e:
            logger.error(f"Failed to parse time: {datetime_str}, Error: {e}")
            return None

    # Make the datetime timezone-aware
    try:
        tz = pytz.timezone(TIME_ZONE)
        return make_aware(final_dt, timezone=tz)
    except Exception as e:
        logger.error(f"Failed to make datetime aware: {final_dt}, Error: {e}")
        return None


@shared_task
def guest_match_data():
    # get all GuestProfile that toast field is empty
    data = GuestProfile.objects.filter(toast=None, matched=GuestProfile.M_INITIAL_MATCHED)
    logger.info(f"start matching {data.count()} guests")
    for item in data:
        data_object = None
        reservation_time = item.reservation_date
        if item.model_name == "Resy":
            data_object = ResyReservation.objects.get(pk=item.object_id)
        elif item.model_name == "Tock":
            data_object = TockBooking.objects.get(pk=item.object_id)
        else:
            logger.info(f"Model {item.model_name} not found")
            continue
        # if item.model_name == "Resy":
        #     # Merge the reservation date and time from Resy into a datetime object
        #     reservation_time = merge_resy_date_time(
        #         data_object.reservation_date, data_object.time)

        #     if reservation_time is None:
        #         logger.warning(
        #             f"Could not parse reservation time for {item} data: {data_object.reservation_date}, {data_object.time}")
        #         continue  # Skip this item if time parsing fails
        # elif item.model_name == "Tock":
        #     reservation_time = data_object.time
        try:
            start_time = reservation_time - timedelta(minutes=15)
            end_time = reservation_time + timedelta(minutes=40)
        except Exception as e:
            logger.error(
                f"Failed to calculate start and end time for {item}, Error: {e}")
            continue

        table_values = (
            (data_object.table if item.model_name == "Resy" else data_object.tables)
            .replace(" ", "")
            .split(",")
        )
        query = Q()
        logger.info(f"check table values: {table_values}")
        for table_value in table_values:
            query |= Q(table=table_value)
        # print Q
        logger.info(f"query table: {query}")
        unit = data_object.resy_auth.unit if item.model_name == "Resy" else data_object.tock.unit
        toast_order = (
            ToastOrder.objects.filter(
                opened__range=(start_time, end_time),
                toast_auth__unit=unit,
                user=None,  # Only update ToastOrder where user is None
            )
            .filter(query)
            # Exclude NULL and empty table
            .exclude(table__isnull=True).exclude(table="")
            .first()
        )
        if toast_order:
            item.toast = toast_order
            item.matched = GuestProfile.M_MATCHED
            item.save()
            logger.info(f"Matched {item} with ToastOrder {toast_order.pk}")
        else:
            item.matched = GuestProfile.M_NOT_MATCHED
            item.save()
            logger.info(f"No ToastOrder found for {item.pk}")
