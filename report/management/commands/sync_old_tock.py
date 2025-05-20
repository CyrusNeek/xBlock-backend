
from django.core.management.base import BaseCommand

from report.models.resy_reservation import ResyReservation
from report.models.tock_booking import TockBooking
from report.tasks.periodic.guest_task import combine_tock_and_resy

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # get all ResyReservation objects and split 100/100 processing
        # fill field first_name,last_name and brand from field user
        # and call combine_tock_and_resy.delay() with data
        tock_data = TockBooking.objects.all()
        tock_data_count = tock_data.count()
        resy_data_half = tock_data_count // 2
        tock_data_first_half = tock_data[:resy_data_half]
        tock_data_second_half = tock_data[resy_data_half:]
        logger.info(
            f"f1 Tock start matching {tock_data_first_half.count()} guests")
        for item in tock_data_first_half:
            if item.user:
                item.first_name = item.user.first_name
                item.last_name = item.user.last_name
                item.email = item.user.email
                item.brand = item.user.brand
                item.phone = item.user.phone
                item.save()
        logger.info(
            f"f2 Tock start matching {tock_data_second_half.count()} guests")
        for item in tock_data_second_half:
            if item.user:
                item.first_name = item.user.first_name
                item.last_name = item.user.last_name
                item.email = item.user.email
                item.brand = item.user.brand
                item.phone = item.user.phone
                item.save()
        combine_tock_and_resy.delay()
