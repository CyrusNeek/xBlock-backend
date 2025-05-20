
from django.core.management.base import BaseCommand

from report.models.resy_reservation import ResyReservation

import logging

from report.tasks.periodic.guest_match import guest_match_data
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        guest_match_data()
