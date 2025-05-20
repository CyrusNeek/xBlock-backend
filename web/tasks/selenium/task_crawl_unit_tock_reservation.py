from celery import shared_task
from web.models import Reservation
from web.models import Unit, Customer
from web.selenium import TockSeleniumCrawler
import logging
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import IntegrityError, transaction

from web.tasks.selenium.util import send_teams_message

logger = logging.getLogger(__name__)


def create_or_update_reservations(unit, reservation_data_list):
    successful_reservations = []
    failed_reservations = []

    for reservation_dict in reservation_data_list:
        try:
            # Convert date and time strings to objects
            reservation_date = datetime.strptime(
                reservation_dict["reservation_date"], "%m/%d/%Y"
            ).date()
            reservation_time = datetime.strptime(
                reservation_dict["reservation_time"], "%I:%M %p"
            ).time()

            # Use update_or_create to handle uniqueness
            obj, created = Reservation.objects.update_or_create(
                email=reservation_dict["email"],
                phone_number=reservation_dict["phone_number"],
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                area=reservation_dict.get("area", ""),
                tables=reservation_dict.get("tables", ""),
                unit=unit,
                defaults={
                    "first_name": reservation_dict["first_name"],
                    "last_name": reservation_dict["last_name"],
                    "party_size": reservation_dict.get("party_size"),
                    "experience": reservation_dict["experience"],
                    "tags": reservation_dict.get("tags", ""),
                    "notes": reservation_dict.get("notes", ""),
                },
            )
            successful_reservations.append(obj)
        except (IntegrityError, ValidationError) as e:
            failed_reservations.append((reservation_dict, str(e)))

    return successful_reservations, failed_reservations


def create_or_update_customer(customer_data):
    """
    Create or update a Customer instance based on the provided data.
    """
    logger.info(f"Creating or updating customers")
    successful_customers = []
    failed_customers = []

    for customer_dict in customer_data:
        try:
            # Use transaction.atomic to ensure database integrity
            with transaction.atomic():
                # Use update_or_create to handle uniqueness, considering email as a unique identifier
                customer, created = Customer.objects.update_or_create(
                    email=customer_dict["email"],
                    defaults={
                        "first_name": customer_dict["first_name"],
                        "last_name": customer_dict["last_name"],
                        "phone_number": customer_dict["phone_number"],
                    },
                )
                successful_customers.append(customer)
        except IntegrityError as e:
            logger.error(f"Error create customer: {e}")
            # Handle cases where the update_or_create could violate database constraints
            failed_customers.append((customer_dict, str(e)))

    return successful_customers, failed_customers


@shared_task
def task_crawl_unit_tock_reservation(unit_id: int, start_date: str, end_date: str):
    """
    Crawl Tock reservation given a unit and date
    """
    # make sure start_date and end_date are in the YYYY-MM-DD format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        logger.error("Date must be in YYYY-MM-DD format. Task abort")
        return

    unit = Unit.objects.get(id=unit_id)
    tock_auth = unit.tock_auth
    logger.info(
        f"crawl tock reservation for unit {unit.name} on {start_date} to {end_date}"
    )
    try:
        # crawl report
        reservations = TockSeleniumCrawler(
            email=tock_auth.email,
            password=tock_auth.password,
            start_date=start_date,
            end_date=end_date,
        ).start()
        send_teams_message(
            title=f"Tock reservations for {unit.name} on {start_date} to {end_date}",
            report=reservations,
        )

        create_or_update_reservations(unit, reservations)
        create_or_update_customer(reservations)

        logger.info(
            f"Successfully crawl Tock reservations for unit {unit.name} on {start_date} to {end_date}"
        )
        return f"{len(reservations)} reservations crawled for unit {unit.name} on {start_date} to {end_date}"
    except Exception as e:
        logger.error(
            f"Failed Crawl toast report for unit {unit.name} on {start_date} to {end_date}: {e}"
        )
        raise e
        # send_teams_message(
        #     title=f"Tock crawl error for {unit.name} on {start_date} to {end_date} {e}",
        #     report=reservations,
        # )
