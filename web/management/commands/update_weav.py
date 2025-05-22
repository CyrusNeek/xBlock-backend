import datetime
from django.core.management.base import BaseCommand, CommandError
import logging
import time

from web.models.unit import Unit
from web.services.weaviate import WeaviateManager
from web.tasks.periodic_tasks.upload_weaviate import insert_orders_to_weaviate, insert_resy_reservations_to_weaviate, insert_tock_bookings_to_weaviate, insert_users_to_weaviate, upload_data_to_weaviate

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--unit', type=int, help='id of the unit')
        # get date (optional)
        parser.add_argument('--date', type=str, help='date to upload data')
        parser.add_argument('--all', type=str, help='date to upload data')

    def handle(self, *args, **options):
        def update_to_weav(manager, unit):
            # get current date
            # get date and parse that
            print("options:", options)
            date = None
            if 'date' in options and options['date']:
                date = datetime.datetime.strptime(options['date'], '%Y-%m-%d')
            elif 'all' in options:
                date = None
            else:
                today = datetime.date.today()
                date = today - datetime.timedelta(days=1)
            insert_users_to_weaviate(manager, unit, date)
            insert_orders_to_weaviate(manager, unit, date)
            insert_tock_bookings_to_weaviate(manager, unit, date)
            insert_resy_reservations_to_weaviate(manager, unit, date)
        manager = WeaviateManager()
        if 'unit' in options and options['unit']:
            unit_id = options['unit']
            unit = Unit.objects.get(pk=unit_id)
            update_to_weav(manager, unit)

        else:
            units = Unit.objects.all()
            # TODO: Add a loop to upload all units
            for unit in units:
                print("INFO: Start uploading data to Weaviate for unit: ", unit)
                update_to_weav(manager, unit)
                print("INFO: End uploading data to Weaviate for unit: ", unit)
                time.sleep(5)
