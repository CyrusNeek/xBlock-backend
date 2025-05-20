
from django.core.management.base import BaseCommand

from report.models.resy_reservation import ResyReservation
from report.tasks.periodic.guest_task import combine_tock_and_resy

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        combine_tock_and_resy()
