
from django.core.management.base import BaseCommand

from report.models.resy_reservation import ResyReservation

import logging

from report.tasks.periodic.toast.toast_crawler import task_fetch_toasts_data
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        task_fetch_toasts_data()
