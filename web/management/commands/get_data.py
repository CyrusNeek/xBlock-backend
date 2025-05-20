from django.core.management.base import BaseCommand, CommandError
import logging
import time

from web.models.unit import Unit
from web.services.weaviate import WeaviateManager
from web.tasks.periodic_tasks.upload_weaviate import insert_orders_to_weaviate, insert_resy_reservations_to_weaviate, insert_tock_bookings_to_weaviate, insert_users_to_weaviate, upload_data_to_weaviate

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        manager = WeaviateManager()
        collection_name = "userProfile"
        # last_recorded_store = manager.get_last_record("userProfile")
        # print("get_last_recorded_store:", last_recorded_store.properties)
        # col = manager.get_collection("userProfile")
        # print("get_collection:", col)
        # for i in col.iterator():
        #     print(i.properties)
        existing_user_uuid = manager.get_object(collection_name, user_id=217391.0)
        print(existing_user_uuid)
        # Print all fetched objects
        # for obj in result:
        # print(obj)
