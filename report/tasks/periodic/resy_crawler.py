from concurrent.futures import ThreadPoolExecutor
from django.db import transaction
from django.conf import settings
from celery import shared_task
import logging
import time
from datetime import datetime, timedelta

import pytz
from report.models import (
    ReportUser,
    ResyAuth,
    ResyReservation,
    ResyRating,
    Tag,
)
from report.models.analytic_report import AnalyticReport
from report.selenium.services.driver import Driver
from report.selenium.services.html import Html
from report.selenium.resy.location import Location
from report.selenium.resy.login import LoginToResy
from report.selenium.resy.reservation import Reservation
from report.selenium.resy.reservation_datetime import ReservationDateTime
from report.selenium.resy.rating import Rating
from report.selenium.resy.rating_datetime import RatingDateTime
from django.utils.timezone import make_aware
from report.tasks.periodic.resy_req import ResyCrawlerAPI
from xblock.settings import TIME_ZONE


logger = logging.getLogger(__name__)


class ResyCrawler(
    Driver,
    Html,
    LoginToResy,
    Location,
    Reservation,
    ReservationDateTime,
    Rating,
    RatingDateTime,
):
    """
    Crawl Resy'.

    Args:
        email (str): email to login to resy
        password (str): password to login to resy
        location_id (str): location id

    Return:
        [{}]

    Usage:
        Check bottom of the file for example usage
    """

    def __init__(self, email, password, location_id: str, driver=None):
        self.driver = driver or self.get_webdriver()
        self.email = email
        self.password = password
        self.location_id = location_id
        self.login_status = False
        self.data = None

    def start(self):
        try:
            self.login()
            time.sleep(1)
            self.select_location()
        except Exception as e:
            logger.info(f"Error found when log in: {str(e)}")
            raise e

    def end(self):
        self.driver.quit()


@shared_task
def get_valid_reservations_resies():
    """
    Get valid reservations from Resy
    Executed every 2 hours (Beat Schedule)
    """
    resy_auth_list = ResyAuth.objects.exclude(status=ResyAuth.FAIL)
    for resy in resy_auth_list:
        get_valid_reservation_dates_and_fetch.delay(resy.pk)
        resy.last_previous_update = datetime.now()
        resy.save()


@shared_task
def get_valid_rating_resies():
    """
    Get valid ratings from Resy
    Executed every 6 AM 1 day of month (Beat Schedule)
    """
    now = datetime.now()
    sleep_time = settings.CRAWL_BASE_CRAWL_SLEEP_IDLE_SECONDS
    resy_auth_list = ResyAuth.objects.exclude(status=ResyAuth.FAIL)
    month_str = now.strftime("%B %Y")

    for resy in resy_auth_list:
        fetch_resy_ratings_date.delay(resy, month_str)
        time.sleep(sleep_time)


@shared_task
def fetch_resy_ratings_date(resy_pk: int, date, crawler=None):
    # TODO: change!
    try:
        resy = ResyAuth.objects.get(resy_pk)
    except ResyAuth.DoesNotExist:
        return
    if crawler is None:
        crawler = ResyCrawler(
            email=resy.email, password=resy.password, location_id=resy.location_id
        )
        crawler.start()

    data = crawler.ratings_data(date)

    # crawler.driver.close()

    records_to_create = []

    for record in data["result"]["all"]:
        user = ReportUser.objects.filter(brand=resy.unit.brand).first()
        tags = record["tags"].split(",")
        tag_list = []

        for tag in tags:
            if tag == "":
                continue
            tag_list.append(
                Tag.objects.get_or_create(
                    name=tag, unit=resy.unit, defaults={
                        "name": tag, "unit": resy.unit}
                )
            )

        records_to_create.append(
            ResyRating(
                resy_auth=resy,
                user=user,
                review_date=datetime.strptime(record["review_date"]),
                guest=record["guest"],
                vip=record["vip"],
                visit_date=datetime.strptime(record["visit_date"]),
                party_size=int(record["party_size"]),
                email=record["email"],
                server=record["server"],
                ratings=record["ratings"],
                tags=tag_list,
                comment=record["comment"],
            )
        )

    ResyRating.objects.bulk_create(records_to_create, ignore_conflicts=True)

    return data["result"]["all"]


@shared_task
def get_valid_ratings_and_fetch(resy_pk: int):
    """
    Get valid ratings from Resy
    Executed from ResyAuthSerializer when a new ResyAuth is created
    """
    try:
        resy = ResyAuth.objects.get(pk=resy_pk)
    except ResyAuth.DoesNotExist:
        return
    crawler = ResyCrawler(
        email=resy.email, password=resy.password, location_id=resy.location_id
    )

    crawler.start()

    data = crawler.get_ratings_datetimes()

    for record in data["result"]:
        try:
            count = fetch_resy_ratings_date(resy.pk, record, crawler)
            AnalyticReport.objects.create_or_override_record(
                record,
                False,
                resy.unit,
                "RESY",
                count,
                "",
            )

        except Exception as e:
            AnalyticReport.objects.create_or_override_record(
                record,
                False,
                resy.unit,
                "RESY",
                0,
                str(e),
            )
            raise e


@shared_task
def fetch_resy_reservations(resy_pk: int, date, crawler=None):
    # clear
    pass


# Refactor
def is_phone_empty(phone):
    return phone is None or phone == "" or phone == "+-" or phone == "+"


def map_date_to_datetime(reservation_date: str, time: str):
    if time and reservation_date:
        # Combine the date (in 'YYYY-MM-DD' format) and time ('HH:MM:SS')
        datetime_str = f"{reservation_date} {time}"

        # Use the correct format for 24-hour time ('%Y-%m-%d %H:%M:%S')
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

        # Make the datetime timezone-aware using the specified timezone
        tz = pytz.timezone(TIME_ZONE)  # Define TIME_ZONE appropriately
        aware_datetime = make_aware(dt, timezone=tz)

        return aware_datetime


START_DATE = datetime(2020, 1, 1)
MAX_WORKERS = 10  # Adjust this as needed
FUTURE_DAYS = 1  # Number of future days to crawl if is_initial_triggered is True
SLEEP_INTERVAL = 10  # Sleep 10 seconds between chunks
CHUNK_SIZE = 10  # Process 10 days at a time
BATCH_SIZE = 10  # Save data every 10 records


@shared_task
def get_valid_reservation_dates_and_fetch(resy_pk: int):
    try:
        resy = ResyAuth.objects.get(pk=resy_pk)
    except ResyAuth.DoesNotExist:
        return

    try:
        # Initialize crawler and authenticate
        crawler = authenticate_resy_crawler(resy)
    except Exception as e:
        handle_error(resy, str(e), "initial")
        raise e

    # Determine the start date based on existing data
    last_reservation = ResyReservation.objects.filter(
        resy_auth=resy).order_by('-datetime').first()

    if last_reservation:
        # Start from the last reservation date minus one day
        logger.info(f"Last reservation found: {last_reservation.datetime}")
        # start_date = last_reservation.datetime.date() - timedelta(days=1)
        # form yesterday
        start_date = datetime.now() - timedelta(days=1)
    else:
        # If no records exist, start from 2020-01-01
        logger.info(
            f"No previous reservations found. Starting from {START_DATE}")
        start_date = START_DATE

    end_date = datetime.now()  # End date is the current day
    # increase 21 days in end_date
    end_date = end_date + timedelta(days=FUTURE_DAYS)
    start_date = start_date.date() if isinstance(
        start_date, datetime) else start_date
    logger.info(f"Starting crawl from {start_date} to {end_date}")
    # Calculate the total number of days to crawl
    days_to_crawl = (end_date.date() - start_date).days
    logger.info(f"Starting crawl from {start_date} for {days_to_crawl} days.")
    # Split the total days into chunks and process each chunk with a delay
    for chunk_start in range(0, days_to_crawl, BATCH_SIZE):
        chunk_end = min(chunk_start + BATCH_SIZE, days_to_crawl)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures_to_day = {
                executor.submit(fetch_and_process_reservation, crawler, resy, start_date, i): i
                for i in range(chunk_start, chunk_end)
            }

            # Process the data and save in batches of BATCH_SIZE immediately
            for future in futures_to_day:
                day_offset = futures_to_day[future]
                try:
                    result = future.result()
                    if result:
                        # Save each batch of 10 records as soon as they are fetched
                        save_resy_reservations(result)

                except Exception as e:
                    logger.error(f"Error processing day {day_offset}: {e}")

            # Sleep for 10 seconds before processing the next chunk
            time.sleep(SLEEP_INTERVAL)
        # store in AnalyticReport
    AnalyticReport.objects.create_or_override_record(
        datetime.now(),
        True,
        resy.unit,
        "RESY",
        ResyReservation.objects.filter(is_new=True).count(),
        "",
    )
    return True


def authenticate_resy_crawler(resy):
    """
    Handles Resy crawler authentication and venue authorization.
    """
    crawler = ResyCrawlerAPI(
        email=resy.email, password=resy.password, location_code=resy.location_id)
    crawler.login()
    crawler.fetch_venues()
    crawler.venue_auth()
    return crawler


def save_resy_reservations(reservations):
    """
    Save the reservations in the database in a batch, ensuring no duplicates.
    """
    with transaction.atomic():
        for record in reservations:
            try:
                ResyReservation.objects.update_or_create(
                    reserve_number=record.reserve_number,
                    defaults={
                        'resy_auth': record.resy_auth,
                        'time': record.time,
                        "first_name": record.first_name,
                        "last_name": record.last_name,
                        "brand": record.brand,
                        'visit_note': record.visit_note,
                        'status': record.status,
                        'party_size': record.party_size,
                        'email': record.email,
                        'phone': record.phone,
                        'guest': record.guest,
                        'service': record.service,
                        'table': record.table,
                        'reservation_date': record.reservation_date,
                        'datetime': record.datetime,
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error saving reservation {record.reserve_number}: {e}")
                logger.inf(f"datetime: {record.datetime} table: {record.table} reservation {record.reserve_number}")


def fetch_and_process_reservation(crawler, resy, start_date, day_offset):
    """
    Fetches and processes a reservation report for a given day offset from 'start_date'.
    Returns a list of ResyReservation objects if successful, or an empty list if no valid data is found.
    """
    future_date = start_date + timedelta(days=day_offset)
    year = future_date.year
    day_of_year = future_date.timetuple().tm_yday
    logger.info(
        f"Fetching reservation for {future_date}, day of year: {day_of_year}")

    try:
        res = crawler.fetch_reservation_report(year, day_of_year)
        logger.info(f"Reservation Report: {res}")
        # Process reservation data
        resy_objects = []
        for item in res:
            if not item or item.get("guest","").lower() == "(walk-in)":
                continue
            reservation = process_reservation_data(resy, item, future_date)
            if reservation:
                resy_objects.append(reservation)
        return resy_objects

    except Exception as e:
        logger.error(f"Error fetching reservation for {future_date}: {e}")
        return []


def parse_last_visit(last_visit_str):
    """
    Parse the 'Last_Visit' field, which may come in various formats.
    We'll assume it's in the format 'YYYY-MM-DD'.
    """
    if not last_visit_str:
        return None
    try:
        return datetime.strptime(last_visit_str, "%Y-%m-%d").date()
    except ValueError:
        return None  # Return None if the format is unrecognized


def process_reservation_data(resy, res, future_date):
    """
    Creates a ResyReservation object from the API response.
    """
    record_name = res["guest"].split(" ")
    first_name = record_name[0] if record_name else None
    last_name = " ".join(record_name[1:]) if len(record_name) > 1 else None

    if is_phone_empty(res["phone"]) and not res["email"]:
        return None

    # report_user = ReportUser.objects.create_safe(
    #     phone=res["phone"],
    #     brand=resy.unit.brand,
    #     email=res["email"],
    #     first_name=first_name,
    #     last_name=last_name,
    # )

    # Map the reservation datetime
    datetime_obj = map_date_to_datetime(
        future_date.strftime("%Y-%m-%d"),  # Use the format 'YYYY-MM-DD'
        res["time"]
    )
    return ResyReservation(
        resy_auth=resy,
        time=res["time"],
        reservation_date=future_date.strftime(
            "%Y-%m-%d"),  # Ensure it's in 'YYYY-MM-DD'
        datetime=datetime_obj,
        table=str(res["table"]),
        visit_note=res["visit_note"] if res['visit_note'] else " ",
        status=res["status"],
        party_size=int(res["party_size"]),
        email=res["email"],
        phone=res["phone"],
        guest=res["guest"],
        service=res["service"],
        reserve_number=res["reserve_number"],
        brand=resy.unit.brand,
        first_name=first_name,
        last_name=last_name,
        allergy_tags=res.get("allergy_tags", ""),
        guest_tags=res.get("Guest_Tags", ""),
        last_visit=parse_last_visit(
            res.get("Last_Visit", "")),  # Parse Last Visit
        # Total Visits (default to 0)
        total_visits=int(res.get("Total_Visits", 0)),
        special_requests=res.get("special_requests", ""),
        guest_notes=res.get("Guest_Notes", ""),
        ticket_type=res.get("ticket_type", ""),
        is_new=True  # Mark as new reservation
    )


def handle_error(resy, error_message, stage):
    """
    Handles error logging and updating the ResyAuth object on failure.
    """
    resy.status = ResyAuth.FAIL
    resy.error_detail = error_message
    resy.save()

    AnalyticReport.objects.create_or_override_record(
        stage,
        False,
        resy.unit,
        "RESY",
        0,
        error_message,
    )


def update_resy_status(resy, records_to_create):
    """
    Updates ResyAuth status and logs the final analytic report.
    """
    resy.status = ResyAuth.VERIFIED
    resy.error_detail = None
    resy.save()

    AnalyticReport.objects.create_or_override_record(
        datetime.now(),
        True,
        resy.unit,
        "RESY",
        len(records_to_create),
        "",
    )
