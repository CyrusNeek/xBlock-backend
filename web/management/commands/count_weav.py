from django.core.management.base import BaseCommand, CommandError
import logging
import time
import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xblock.settings")


django.setup()


from web.services.weaviate import WeaviateManager
from weaviate.classes.config import Property, DataType, ReferenceProperty, Configure


logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        manager = WeaviateManager()
        # for i in col.iterator():
        #  print(i.properties)
        col_tockBookings = manager.get_collection("tockBookings")
        col_userProfile = manager.get_collection("userProfile")
        col_resyReservations = manager.get_collection("resyReservations")
        col_orders = manager.get_collection("orders")
        print("Total of tockBookings: ", len(col_tockBookings))
        print("Total of userProfile: ", len(col_userProfile))
        print("Total of resyReservations: ", len(col_resyReservations))
        print("Total of orders: ", len(col_orders))