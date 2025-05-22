from django.core.management.base import BaseCommand, CommandError
import logging
import time
import django
import os

from report.models.resy_reservation import ResyReservation
from report.models.toast_order import ToastOrder
from report.models.tock_booking import TockBooking


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xblock.settings")


django.setup()


from report.models.guest_profile import GuestProfile
from web.services.weaviate import WeaviateManager
from weaviate.classes.config import Property, DataType, ReferenceProperty, Configure


logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument('start_date', type=str, help='Start date (MM-DD-YYYY)')
        # parser.add_argument('end_date', type=str, help='End date (MM-DD-YYYY)')
        # parser.add_argument('unit_name', type=str, help='Name of the unit')


    # def create_unitfile_collection(manager: WeaviateManager):
    #     manager.empty_collection(
    #         "unitFile",
    #         [
    #             Property(name="unit", data_type=DataType.INT),
    #             Property(name="block_category", data_type=DataType.INT),
    #             Property(name="name", data_type=DataType.TEXT),
    #             Property(name="summary", data_type=DataType.TEXT),
    #             Property(name="text", data_type=DataType.TEXT),
    #             Property(name="created_at", data_type=DataType.DATE),
    #             Property(name="unit", data_type=DataType.INT),
    #             Property(name="unit_name", data_type=DataType.TEXT),
    #             Property(name="ai_description", data_type=DataType.TEXT),
    #         ],
    #         vectorizer_config=[
    #             Configure.NamedVectors.text2vec_openai(
    #                 name="ai_description", source_properties=["ai_description"]
    #             )
    #         ],
    #     )


    # def create_unitfile_image(manager: WeaviateManager):
    #     manager.empty_collection(
    #         "unitFileImage",
    #         [
    #             Property(name="unit", data_type=DataType.INT),
    #             Property(name="block_category", data_type=DataType.INT),
    #             Property(name="image", data_type=DataType.BLOB),
    #             Property(name="description", data_type=DataType.TEXT),
    #             Property(name="unitfile_name", data_type=DataType.TEXT),
    #             Property(name="unitfile", data_type=DataType.INT),
    #             Property(name="date", data_type=DataType.DATE),
    #             Property(name="ai_description", data_type=DataType.TEXT),
    #         ],
    #         None,
    #         vectorizer_config=[
    #             Configure.Vectorizer.img2vec_neural(["image"]),
    #             Configure.NamedVectors.text2vec_openai(
    #                 name="ai_description", source_properties=["ai_description"]
    #             ),
    #         ],
    #     )




    def handle(self, *args, **options):
        def create_orders_collection(manager: WeaviateManager):
            manager.empty_collection(
                "orders",
                [
                    Property(name="unit", data_type=DataType.INT),
                    Property(name="block_category", data_type=DataType.INT),
                    Property(name="order_id", data_type=DataType.INT),
                    Property(name="order_number", data_type=DataType.INT),
                    Property(name="checks", data_type=DataType.TEXT),
                    Property(name="opened", data_type=DataType.DATE),
                    Property(name="number_of_guests", data_type=DataType.INT),
                    Property(name="tab_names", data_type=DataType.TEXT),
                    Property(name="table", data_type=DataType.TEXT),
                    Property(name="amount", data_type=DataType.NUMBER),
                    Property(name="discount_amount", data_type=DataType.NUMBER),
                    Property(name="service", data_type=DataType.TEXT),
                    Property(name="tax", data_type=DataType.NUMBER),
                    Property(name="tip", data_type=DataType.NUMBER),
                    Property(name="gratuity", data_type=DataType.NUMBER),
                    Property(name="total", data_type=DataType.NUMBER),
                    Property(name="ai_description", data_type=DataType.TEXT),
                    Property(name="created_at", data_type=DataType.DATE),

                ],
                [ReferenceProperty(name="user", target_collection="userProfile")],
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_openai(
                        name="ai_description", source_properties=["ai_description"]
                    )
                ],
            )


        def create_report_users_collection(manager: WeaviateManager):
            manager.empty_collection(
                "userProfile",
                [
                    Property(name="user_id", data_type=DataType.NUMBER),
                    Property(name="email", data_type=DataType.TEXT),
                    Property(name="phone", data_type=DataType.TEXT),
                    Property(name="first_name", data_type=DataType.TEXT),
                    Property(name="last_name", data_type=DataType.TEXT),
                    Property(name="brand", data_type=DataType.INT),
                    Property(name="created_at", data_type=DataType.DATE),
                ],
            )


        def create_resy_reservations_collection(manager: WeaviateManager):
            manager.empty_collection(
                "resyReservations",
                [
                    Property(name="unit", data_type=DataType.INT),
                    Property(name="block_category", data_type=DataType.INT),
                    Property(name="id_resy_reservations", data_type=DataType.NUMBER),
                    Property(name="time", data_type=DataType.TEXT),
                    Property(name="datetime", data_type=DataType.DATE),
                    Property(name="service", data_type=DataType.TEXT),
                    Property(name="guest", data_type=DataType.TEXT),
                    Property(name="phone", data_type=DataType.TEXT),
                    Property(name="email", data_type=DataType.TEXT),
                    Property(name="party_size", data_type=DataType.INT),
                    Property(name="status", data_type=DataType.TEXT),
                    Property(name="table", data_type=DataType.TEXT),
                    Property(name="visit_note", data_type=DataType.TEXT),
                    Property(name="reserve_number", data_type=DataType.TEXT),
                    Property(name="ai_description", data_type=DataType.TEXT),
                    Property(name="created_at", data_type=DataType.DATE),

                ],
                # [ReferenceProperty(name="user", target_collection="userProfile")],
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_openai(
                        name="ai_description", source_properties=["ai_description"]
                    )
                ],
            )


        def create_tock_bookings_collection(manager: WeaviateManager):
            manager.empty_collection(
                name="tockBookings",
                fields=[
                    Property(name="unit", data_type=DataType.INT),
                    Property(name="block_category", data_type=DataType.INT),
                    Property(name="id_tock_booking", data_type=DataType.NUMBER),
                    Property(name="time", data_type=DataType.DATE),
                    Property(name="status", data_type=DataType.TEXT),
                    Property(name="tags", data_type=DataType.TEXT),
                    Property(name="postal_code", data_type=DataType.TEXT),
                    Property(name="party_size", data_type=DataType.TEXT),
                    Property(name="booking_owner", data_type=DataType.TEXT),
                    Property(name="experience", data_type=DataType.TEXT),
                    Property(name="price_per_person", data_type=DataType.NUMBER),
                    Property(name="supplements", data_type=DataType.TEXT),
                    Property(name="question_answers", data_type=DataType.TEXT),
                    Property(name="visit_notes", data_type=DataType.TEXT),
                    Property(name="visit_dietary_notes", data_type=DataType.TEXT),
                    Property(name="guest_providede_order_notes", data_type=DataType.TEXT),
                    Property(name="guest_notes", data_type=DataType.TEXT),
                    Property(name="dietary_notes", data_type=DataType.TEXT),
                    Property(name="total_price", data_type=DataType.NUMBER),
                    Property(name="gross_amount_paid", data_type=DataType.NUMBER),
                    Property(name="net_amount_paid", data_type=DataType.NUMBER),
                    Property(name="service_charge", data_type=DataType.NUMBER),
                    Property(name="gratuity", data_type=DataType.NUMBER),
                    Property(name="visits", data_type=DataType.INT),
                    Property(name="tables", data_type=DataType.TEXT),
                    Property(name="servers", data_type=DataType.TEXT),
                    Property(name="booking_method", data_type=DataType.TEXT),
                    Property(name="spouse_name", data_type=DataType.TEXT),
                    Property(name="ai_description", data_type=DataType.TEXT),
                    Property(name="timezone", data_type=DataType.TEXT),
                    Property(name="created_at", data_type=DataType.DATE),

                ],
                references=[ReferenceProperty(name="user", target_collection="userProfile")],
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_openai(
                        name="embed_time",
                        source_properties=["time"],
                    )
                ],
            )

        manager = WeaviateManager()

        create_report_users_collection(manager)
        create_orders_collection(manager)
        create_tock_bookings_collection(manager)
        create_resy_reservations_collection(manager)
        GuestProfile.objects.update(uploaded=False)
        ToastOrder.objects.update(uploaded=False)
        ResyReservation.objects.update(uploaded=False)
        TockBooking.objects.update(uploaded=False)