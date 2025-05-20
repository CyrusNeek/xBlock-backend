import logging
import time

from datetime import datetime

from report.models import (
    ReportUser,
    ResyAuth,
    ResyReservation,
    ResyRatingSummary,
    ResyRating,
    Tag,
)
from report.tasks.periodic.resy_crawler import *
from report.selenium.services.driver import Driver
from report.selenium.services.html import Html
from report.selenium.resy.location import Location
from report.selenium.resy.login import LoginToResy
from report.selenium.resy.reservation import Reservation
from report.selenium.resy.reservation_datetime import ReservationDateTime
from report.selenium.resy.rating import Rating
from report.selenium.resy.rating_datetime import RatingDateTime

from django.conf import settings
from datetime import datetime


logger = logging.getLogger(__name__)


def main():
    resy = ResyAuth.objects.first()
    try:
        crawler = ResyCrawler(
            email=resy.email, password=resy.password, location_id=resy.location_id
        )
        crawler.start()

        data = crawler.get_reservations_datetimes()

        # crawler.driver.close()

    except Exception as e:
        resy.status = ResyAuth.FAIL
        resy.error_detail = str(e)
        resy.save()

        raise e

    if data["status"] == False:
        raise Exception("Error found for fetching data from Resy")

    dates_datetime = [
        datetime.strptime(date, "%A %B %d, %Y") for date in data["result"]
    ]

    sorted_dates = sorted(dates_datetime, reverse=True)

    sorted_dates_str = [date.strftime("%A %B %d, %Y") for date in sorted_dates]

    # for record in sorted_dates_str:
    #     fetch_resy_reservations(resy.pk, record, crawler.driver)


if __name__ == "django.core.management.commands.shell":
    main()
