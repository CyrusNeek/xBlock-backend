
from django.core.management.base import BaseCommand

from report.models.resy_reservation import ResyReservation
from report.tasks.periodic.guest_task import combine_tock_and_resy
from django.utils.dateparse import parse_datetime

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        resy_res = ResyReservation.objects.all()
        for item in resy_res:
            item.datetime = parse_datetime(f"{item.reservation_date} {item.time}")
            item.save()
