import datetime
from django.core.management.base import BaseCommand, CommandError
import logging
import time

from report.models.tock_auth import TockAuth
from report.tasks.periodic.tock_crawler import crawl_tock_from_past


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--tock', type=int, help='id of the Tock')
        # get date (optional)
        parser.add_argument('--date', type=str, help='date to upload data')
        parser.add_argument('--all', type=str, help='date to upload data')

    def handle(self, *args, **options):
        def crawl(tock_auth):
            crawl_tock_from_past(tock_auth.pk)
            tock_auth.status = TockAuth.PENDING
            tock_auth.error_detail = ""
            tock_auth.save()

        if 'tock' in options and options['tock']:
            tock_id = options['tock']
            try:
                tock_auth = TockAuth.objects.get(pk=tock_id)
            except TockAuth.DoesNotExist:
                print("TockAuth not found", tock_id)
                exit(0)
            print("INFO: start crawling Tock for unit: ", tock_auth.unit)
            crawl(tock_auth)
        else:
            tocks = TockAuth.objects.all()
            for tock_auth in tocks:
                print("INFO: start crawling Tock for unit: ", tock_auth.unit)
                crawl(tock_auth)
                print("INFO: end crawling Tock for unit: ", tock_auth.unit)
                time.sleep(5)
