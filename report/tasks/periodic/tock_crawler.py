import os
import tempfile
from celery import shared_task
from django.utils.timezone import datetime, timedelta
from django.db.utils import IntegrityError

import logging
import time
from django.utils.dateparse import parse_date
from report.models import TockAuth, TockBooking, ReportUser, Tag, AnalyticReport
from report.selenium.services.driver import Driver
from report.selenium.services.html import Html
from report.selenium.services.excel import Excel
from report.selenium.tock.navigate import Navigate
from report.selenium.tock.location import Location
from report.selenium.tock.login import LoginToTock
from report.selenium.tock.date_picker import DatePicker
from report.selenium.tock.status import Status
from report.selenium.tock.download import Download
from django.conf import settings

import pandas as pd

import math
import shutil
from xblock.settings import DAY_TOCK  # Import Django's timezone utilities


def clear_directory(path):
    # Step 2: Iterate over the contents of the directory
    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # Step 3: Check if it's a file or directory
        if os.path.isfile(item_path):
            os.remove(item_path)  # Remove the file
            print(f"Removed file: {item_path}")
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove the directory and its contents
            print(f"Removed directory: {item_path}")


def parse_date(date_str, format="%m/%d/%y %I:%M %p"):
    if type(date_str) == float and math.isnan(date_str):
        return None
    return datetime.strptime(date_str, format)


def is_safe_value(value):
    if type(value) == float and math.isnan(value):
        return False

    if not value:
        return False

    return True


def safe_float(value):
    try:
        return float(value) if pd.notnull(value) or not math.isnan(value) else None
    except ValueError:
        return None


logger = logging.getLogger(__name__)


def split_dates(start_date, end_date):
    chunks = []
    # Split the date range into 60-day chunks
    current_start_date = start_date
    while current_start_date < end_date:
        current_end_date = min(current_start_date +
                               timedelta(days=60), end_date)
        chunks.append((current_start_date, current_end_date))
        current_start_date = current_end_date + timedelta(days=1)
    return chunks


class TockCrawler(
    Driver, Html, LoginToTock, Navigate, Location, DatePicker, Status, Download, Excel
):
    """
    Crawl Tock reservation record given auth, start_date and end_date 'YYYY-MM-DD'.

    Args:
        email (str): email to login to toast
        password (str): password to login to toast
        start_date (str): start date of reservations
        end_date (str): end date of reservations

    Return:
        [{}]

    Usage:
        Check bottom of the file for example usage
    """

    def __init__(
        self, email, password, location_id: str, start_date: str, end_date: str
    ):
        self.path = tempfile.mkdtemp()
        self.driver = self.get_webdriver(self.path)
        self.email = email
        self.password = password
        self.location_id = location_id
        self.login_status = False
        self.data = None
        self.start_date = start_date
        self.end_date = end_date

    def start(self):
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        self.login()
        self.navigate_to_operations_page()
        time.sleep(1)
        self.select_location()
        time.sleep(1)

        res = {"status": True, "result": []}
        logger.info("path is:", self.path)
        if end_date > start_date + timedelta(days=DAY_TOCK):
            chunks = self.chunk_date_range(start_date, end_date)
            all_data = []
            for chunk_start, chunk_end in chunks:
                logger.info(f"end_date > start_date + timedelta(days=DAY_TOCK) Data is: {type(res)} and {res}",)
                
                res = self.start_chunk(chunk_start, chunk_end)
                break
                
                # res["status"] = data["status"]

                # if data["status"] is False:
                #     return data
                # # res["result"] = [*res["result"], data["result"]]
                # if isinstance(data["result"], pd.DataFrame):
                #     res["result"] = pd.concat([res["result"], data["result"]], ignore_index=True)
                # else:
                #     logger.warning("Chunk result is not a DataFrame")
                #     continue

            shutil.rmtree(self.path)
            try:
                self.driver.quit()
            except Exception:
                pass

            return res
        else:
            res = self.start_chunk(start_date, end_date)
            logger.info("end_date < start_date + timedelta(days=DAY_TOCK) Data is:", res)
            shutil.rmtree(self.path)
            try:
                self.driver.quit()
            except Exception:
                pass

            return res

    def start_chunk(self, start_date, end_date):
        self.start_date = start_date.strftime("%Y-%m-%d")
        self.end_date = end_date.strftime("%Y-%m-%d")

        data = dict()
        data["status"] = True

        try:
            self.select_date()
            logger.info("Selecting statuses")
            self.select_all_status()
            logger.info("Downloading the excel")
            self.download_excel()
            time.sleep(30)

            data["result"] = self.load_any_file_in_dir(
                self.path + "/Downloads",
            )
            try:
                clear_directory(self.path)
            except Exception:
                pass

        except Exception as e:
            logger.info(e)
            data["status"] = False
            data["result"] = []
            data["error"] = e

        return data

    def chunk_date_range(self, start_date, end_date):
        chunks = []
        current_start_date = start_date
        while current_start_date < end_date:
            current_end_date = min(
                current_start_date + timedelta(days=60), end_date
            )
            chunks.append((current_start_date, current_end_date))
            current_start_date = current_end_date + timedelta(days=1)
        return chunks


# if __name__ == "__main__":

#     today_str = datetime.now().strftime('%Y-%m-%d')
# data = TockCrawler(
#     "dena@xblock.ai",
#     "YbLznxJ51bo2uTgJ6QZ7#",
#     str(24416),
#     today_str,
#     today_str).start()

#     print(data)


@shared_task
def crawl_tocks():
    """
    Crawls through all TockAuth objects and triggers periodic or past crawling tasks.
    This function retrieves all TockAuth objects and iterates through them. For each TockAuth object,
    it checks if the initial trigger has been set. If it has, it triggers the `crawl_tock_periodic` task.
    Otherwise, it triggers the `crawl_tock_from_past` task. After processing each TockAuth object, the
    function sleeps for a specified duration.
    Note:
        The sleep duration is determined by the `CRAWL_BASE_CRAWL_SLEEP_IDLE_SECONDS` setting.
    Tasks:
        - `crawl_tock_periodic`: Triggered if the TockAuth object has the initial trigger set.
        - `crawl_tock_from_past`: Triggered if the TockAuth object does not have the initial trigger set.
    Raises:
        None
    Returns:
        None
    """
    tocks = TockAuth.objects.filter(status=TockAuth.VERIFIED)
    sleep_time = settings.CRAWL_BASE_CRAWL_SLEEP_IDLE_SECONDS

    for tock in tocks:
        if tock.is_initial_triggered:
            crawl_tock_periodic.delay(tock)

        else:
            crawl_tock_from_past.delay(tock.pk)

        time.sleep(sleep_time)


def save_tock_bookings(transactions, tock: TockAuth):
    records_to_create = []
    for record in transactions:
        date_str = record["Date"]
        time_str = record["Time"]
        datetime_str = f"{date_str} {time_str}"

        try:
            time_obj = datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
        except Exception:
            time_obj = None

        email = record.get("Email")
        phone = record.get("Phone")
        first_name = record.get("First Name")
        last_name = record.get("Last Name")

        status_map = {
            "Available": TockBooking.BookStatus.AVAILABLE.value,
            "Canceled": TockBooking.BookStatus.CANCELED.value,
            "Booked": TockBooking.BookStatus.BOOKED.value,
        }

        status = status_map.get(
            record["Status"], TockBooking.BookStatus.AVAILABLE.value
        )

        if record["Status"] == "Available":
            continue  # Skip this record if a duplicate exists

        # report_user = ReportUser.objects.create_safe(
        #     email=email,
        #     phone=phone,
        #     brand=tock.unit.brand,
        #     first_name=first_name,
        #     last_name=last_name,
        # )

        guest_tags = []
        visit_tags = []

        if record["Guest Tags"] and pd.notnull(record["Guest Tags"]):
            tag = record["Guest Tags"]

            if type(record["Guest Tags"]) == float:
                guest_tags.append(
                    Tag.objects.get_or_create(
                        name=str(tag), defaults={"user": tock})[0]
                )

            else:
                for tag in record["Guest Tags"].split(","):
                    guest_tags.append(
                        Tag.objects.get_or_create(
                            name=tag.strip(), defaults={"user": tock}
                        )[0]
                    )

        if record["Visit Tags"] and pd.notnull(record["Visit Tags"]):
            tag = record["Visit Tags"]

            if type(record["Visit Tags"]) == float:
                visit_tags.append(
                    Tag.objects.get_or_create(
                        name=str(tag), defaults={"user": tock})[0]
                )

            else:
                for tag in record["Visit Tags"].split(","):
                    visit_tags.append(
                        Tag.objects.get_or_create(
                            name=tag.strip(), defaults={"user": tock}
                        )[0]
                    )

        # visit_tags = [Tag.objects.get_or_create(name=tag.strip())[0] for tag in record['Visit Tags'].split(',')] if record['Visit Tags'] else []

        booking = TockBooking.objects.filter(
            confirmation=record["Confirmation"]).first()

        if booking is None:
            booking = TockBooking()

        booking.tock = tock
        booking.report_triggered_at = datetime.now()
        booking.time = time_obj
        booking.status = status
        booking.postal_code = record["Postal Code"]
        booking.booking_owner = record["Booking Owner"]
        # booking.user = report_user
        booking.email=email,
        booking.phone=phone,
        booking.brand=tock.unit.brand,
        booking.first_name=first_name,
        booking.last_name=last_name,
        booking.experience = record["Experience"]
        booking.price_per_person = safe_float(record["Price Per Person"])
        booking.supplements = record["Supplements"]
        booking.question_answers = record["Question Answers"]
        booking.visit_notes = record["Visit notes"]
        booking.visit_dietary_notes = record["Visit dietary notes"]
        booking.guest_provided_order_notes = record["Guest-provided order notes"]
        booking.guest_notes = record["Guest notes"]
        booking.dietary_notes = record["Dietary notes"]
        booking.total_price = safe_float(record["Total Price"])
        booking.gross_amount_paid = safe_float(record["Gross amount paid"])
        booking.net_amount_paid = safe_float(record["Net amount paid"])
        booking.service_charge = safe_float(record["Service Charge"])
        booking.gratuity = safe_float(record["Gratuity"])
        booking.confirmation = record["Confirmation"]
        booking.visits = safe_float(record["Visits"])
        booking.last_visit_date = (
            parse_date(record["Last Visit Date"], "%Y-%m-%d")
            if record["Last Visit Date"]
            else None
        )
        booking.last_visit_time = (
            parse_date(record["Last Visit Time"], "%I:%M %p").time()
            if is_safe_value(record["Last Visit Time"])
            else None
        )
        booking.group_visits = (
            int(record["Group Visits"]) if pd.notnull(
                record["Group Visits"]) else 0
        )
        booking.last_group_visit_date = (
            parse_date(record["Last Group Visit Date"], "%Y-%m-%d")
            if record["Last Group Visit Date"]
            else None
        )
        booking.last_group_visit_time = (
            parse_date(record["Last Group Visit Time"], "%I:%M %p").time()
            if is_safe_value(record["Last Group Visit Time"])
            else None
        )
        booking.last_group_visit_restaurant = record["Last Group Visit Restaurant"]
        booking.spouse_name = record["Spouse Name"]
        booking.birthday = (
            parse_date(record["Birthday"], "%Y-%m-%d")
            if record["Birthday"]
            else None
        )
        booking.booking_method = record["Booking Method"]
        booking.modified_by = record["Modified By"]
        booking.final_status = record["Final Status"]
        booking.tables = (
            record["Tables"].replace(" ", "")
            if pd.notnull(record["Tables"]) and type(record['Tables']) != int
            else str(record['Tables']) if type(record['Tables']) == int else ""
        )
        booking.servers = record["Servers"]
        booking.dining_time_seconds = (
            safe_float(record["Dining Time (seconds)"])
            if record["Dining Time (seconds)"]
            else 0
        )

        records_to_create.append(booking)

        try:
            booking.save()

            # Adding ManyToMany relationships after saving the instance
            for tag in guest_tags:
                booking.guest_tags.add(tag)
            for tag in visit_tags:
                booking.visit_tags.add(tag)
        except IntegrityError:
            pass

    return len(records_to_create)
    # TockBookings.objects.bulk_create(records_to_create)


@shared_task
def crawl_tock_bookings_by_date(tock_pk: int, start, end):
    """
    Crawls Tock bookings for a given date range and saves the results.
    Args:
        tock_pk (int): Primary key of the TockAuth object.
        start (datetime): Start date for the bookings to be crawled.
        end (datetime): End date for the bookings to be crawled.
    Raises:
        TockAuth.DoesNotExist: If the TockAuth object with the given primary key does not exist.
        Exception: If an error occurs during the crawling process or if the data contains an error.
    Returns:
        None
    """
    try:
        tock = TockAuth.objects.get(pk=tock_pk)
    except TockAuth.DoesNotExist:
        logger.error(
            "crawl_tock_bookings_by_date: TockAuth not found", tock_pk)
        return
    logger.info(
        f"start crawl data from {start} to {end} and location id: {tock.location_id}")
    try:
        data = TockCrawler(
            tock.email,
            tock.password,
            tock.location_id,
            start,
            end,
        ).start()
    except Exception as e:
        tock.status = tock.FAIL
        tock.error_detail = str(e)
        tock.save()
        AnalyticReport.objects.create_or_override_record(
            "initial" if not tock.is_initial_triggered else datetime.now(
            ), False, tock.unit, "TOCK", 0, str(e)
        )
        logger.error("Error while crawling tock bookings by date", e)
        raise e
    logger.info(
        "crawl_tock_bookings_by_date: the data is check the data has error", data)
    try:
        if isinstance(data, list) and len(data) == 0:
            logger.info("crawl_tock_bookings_by_date: no data found")
            AnalyticReport.objects.create_or_override_record(
                end,
                True,
                tock.unit,
                "TOCK",
                0,
            )
            tock.status = tock.VERIFIED
            tock.save()
            return
        if hasattr(data, "get") and data.get("error"):
            logger.info(f"the data has hasattr and error {data['']}",)
            tock.status = tock.FAIL
            tock.error_detail = str(data.get("error"))
            tock.save()

            AnalyticReport.objects.create_or_override_record(
                "initial" if not tock.is_initial_triggered else datetime.now(
                ), False, tock.unit, "TOCK", 0, data["error"]
            )
            raise data["error"]
        # Function to save data to the database
        df = None

        # Check if the data is a list and extract the first element's 'result'
        if isinstance(data, list) and len(data) > 0:
            logger.info("log first and data is list")
            df = data[0].get("result", None)

        # Check if the data is a dictionary and extract its 'result'
        elif isinstance(data, dict):
            logger.info("the data is a dict")
            df = data.get("result", None)

        # Ensure df is a DataFrame and it's not empty
        if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
            logger.info(f"df is a DataFrame and its shape is {df.shape}")
            
            # Convert the DataFrame to a list of dictionaries
            transactions = df.to_dict(orient="records")
            
            # Log and save the data in the database
            logger.info(f"First 5 transactions: {transactions[:5]}")
            
            # Call your database save function
            length_data_store = save_tock_bookings(transactions, tock)
            AnalyticReport.objects.create_or_override_record(
                end,
                True,
                tock.unit,
                "TOCK",
                length_data_store,
                "Success"
            )
            tock.status = tock.VERIFIED
            tock.save()
        else:
            logger.info(f"Data received: {data} of type {type(data)}")
            logger.info("crawl_tock_bookings_by_date: no data found")
            AnalyticReport.objects.create_or_override_record(
                end,
                True,
                tock.unit,
                "TOCK",
                0,
                "crawl_tock_bookings_by_date: no data found"
            )
    except Exception as e:
        tock.status = tock.FAIL
        tock.error_detail = str(e)
        tock.save()
        logger.info("crawl_tock_bookings_by_date: error while saving data", e)


@shared_task(max_retries=2, default_retry_delay=10)
def crawl_tock_from_past(tock_id: int):
    """
        Crawl Tock data from the past and update the database.
        This task retrieves booking data from Tock starting from the last crawled date
        or from January 1, 2021, if no previous data exists. It splits the date range
        into chunks and triggers asynchronous tasks to crawl bookings for each chunk.
        Args:
            tock (TockAuth): An instance of TockAuth containing authentication and
                            configuration details for the Tock service.
        Returns:
            None
        Side Effects:
            - Updates the TockAuth instance with error details and status if no location ID is provided.
            - Creates or overrides an AnalyticReport record with the status of the crawl.
            - Triggers asynchronous tasks to crawl bookings for each date chunk.
    """
    try:
        tock = TockAuth.objects.get(pk=tock_id)
    except TockAuth.DoesNotExist:
        logger.error("TockAuth not found", tock_id)
        return
    if tock.location_id is None:
        tock.error_detail = "No tock location id provided"
        tock.status = TockAuth.FAIL
        tock.save()
        AnalyticReport.objects.create_or_override_record(
            "initial" if not tock.is_initial_triggered else datetime.now(
            ), False, tock.unit, "TOCK", 0, "No tock location id provided"
        )
        logger.error("No tock location id provided", tock.pk)
        return

    # get last date of crawled from TockBooking with time field if empty get data from 2021,01,01
    # last_data = TockBooking.objects.filter(tock=tock).order_by("-time").first()
    far_past = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=DAY_TOCK)

    # if last_data:
    #     last_date = last_data.time

    #     # Get current timezone-aware time
    #     current_time = timezone.now()

    #     if last_date and last_date < current_time:
    #         end_date = last_date + timedelta(days=60)
    #         far_past = last_date
    #     else:
    #         far_past = datetime.now()
    #         end_date += timedelta(days=60)
    # else:
    #     far_past = datetime(year=2021, month=1, day=1)

    dates = split_dates(far_past, end_date)

    for chunk_start, chunk_end in dates:
        logger.info(
            f"Trigger: start crawling tock bookings by date, {chunk_start} - {chunk_end}")
        crawl_tock_bookings_by_date.delay(
            tock.pk,
            chunk_start.strftime("%Y-%m-%d"),
            chunk_end.strftime("%Y-%m-%d"),
        )

    # try:
    #     data = TockCrawler(
    #         tock.email,
    #         tock.password,
    #         tock.location_id,
    #         far_past.strftime("%Y-%m-%d"),
    #         now,
    #     ).start()
    # except Exception as e:
    #     tock.status = tock.FAIL
    #     tock.error_detail = str(e)
    #     tock.save()

    #     AnalyticReport.objects.create_or_override_record(
    #         "initial", False, tock.unit, "TOCK", 0, str(e)
    #     )
    #     raise e

    # if data.get("error"):
    #     tock.status = tock.FAIL
    #     tock.error_detail = str(data.get("error"))
    #     tock.save()

    #     AnalyticReport.objects.create_or_override_record(
    #         "initial", False, tock.unit, "TOCK", 0, data["error"]
    #     )
    #     raise data["error"]

    # df = data["result"]

    # transactions = df.to_dict(orient="records")

    # save_tock_bookings(transactions, tock)

    # tock.is_initial_triggered = True

    # tock.last_previous_update = now

    # tock.save()

    # AnalyticReport.objects.create_or_override_record(
    #     "initial",
    #     True,
    #     tock.unit,
    #     "TOCK",
    #     len(transactions),
    # )


@shared_task(max_retries=2, default_retry_delay=100)
def crawl_tock_periodic(tock: TockAuth):
    if tock.location_id is None:
        tock.error_detail = "No tock location id provided"
        tock.status = TockAuth.FAIL
        tock.save()
        return

    if not tock.last_previous_update:
        tock.last_previous_update = datetime.now()

    previous_date = tock.last_previous_update - timedelta(days=1)
    now = (datetime.now() + timedelta(days=DAY_TOCK)).strftime("%Y-%m-%d")
    try:
        data = TockCrawler(
            tock.email,
            tock.password,
            tock.location_id,
            previous_date.strftime("%Y-%m-%d"),
            now,
        ).start()
    except Exception as e:
        tock.status = tock.FAIL
        tock.error_detail = str(e)
        AnalyticReport.objects.create_or_override_record(
            previous_date.strftime("%Y-%m-%d"),
            False,
            tock.unit,
            "TOCK",
            0,
            str(e),
        )
        tock.save()
        raise e
    logger.info(f"Tock: the data is {data}")
    if data["status"] == False:
        tock.status = tock.FAIL
        tock.error_detail = str(data["error"])
        AnalyticReport.objects.create_or_override_record(
            previous_date.strftime("%Y-%m-%d"),
            False,
            tock.unit,
            "TOCK",
            0,
            str(data["error"]),
        )
        tock.save()

        raise data["error"]

    df = data["result"]

    transactions = df.to_dict(orient="records")

    save_tock_bookings(transactions, tock)
    tock.status = TockAuth.VERIFIED
    tock.error_detail = None
    tock.last_previous_update = now

    AnalyticReport.objects.create_or_override_record(
        previous_date.strftime("%Y-%m-%d"),
        True,
        tock.unit,
        "TOCK",
        len(transactions),
        "",
    )

    tock.save()
