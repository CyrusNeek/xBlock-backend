
from django.core.management.base import BaseCommand

from report.models.guest_profile import Guest, GuestProfile
from report.models.resy_reservation import ResyReservation

import logging

from report.models.tock_booking import TockBooking
from report.tasks.periodic.guest_match import guest_match_data
from report.tasks.periodic.guest_task import lifetime_calculate
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        lifetime_calculate()