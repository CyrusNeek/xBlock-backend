# import django
# import os


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xblock.settings")


# django.setup()


# from web.services.weaviate import WeaviateManager
# from weaviate.classes.config import Property, DataType, ReferenceProperty, Configure


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
#         Configure.Vectorizer.img2vec_neural(["image"]),
#         vectorizer_config=[
#             Configure.NamedVectors.text2vec_openai(
#                 name="ai_description", source_properties=["ai_description"]
#             )
#         ],
#     )


# def create_orders_collection(manager: WeaviateManager):
#     manager.empty_collection(
#         "orders",
#         [
#             Property(name="unit", data_type=DataType.INT),
#             Property(name="block_category", data_type=DataType.INT),
#             Property(name="order_id", data_type=DataType.INT),
#             Property(name="order_number", data_type=DataType.INT),
#             Property(name="checks", data_type=DataType.TEXT),
#             Property(name="opened", data_type=DataType.DATE),
#             Property(name="number_of_guests", data_type=DataType.INT),
#             Property(name="tab_names", data_type=DataType.TEXT),
#             Property(name="table", data_type=DataType.TEXT),
#             Property(name="amount", data_type=DataType.NUMBER),
#             Property(name="discount_amount", data_type=DataType.NUMBER),
#             Property(name="service", data_type=DataType.TEXT),
#             Property(name="tax", data_type=DataType.NUMBER),
#             Property(name="tip", data_type=DataType.NUMBER),
#             Property(name="gratuity", data_type=DataType.NUMBER),
#             Property(name="total", data_type=DataType.NUMBER),
#             Property(name="ai_description", data_type=DataType.TEXT),
#         ],
#         [ReferenceProperty(name="user", target_collection="userProfile")],
#         vectorizer_config=[
#             Configure.NamedVectors.text2vec_openai(
#                 name="ai_description", source_properties=["ai_description"]
#             )
#         ],
#     )


# def create_report_users_collection(manager: WeaviateManager):
#     manager.empty_collection(
#         "userProfile",
#         [
#             Property(name="email", data_type=DataType.TEXT),
#             Property(name="phone", data_type=DataType.TEXT),
#             Property(name="first_name", data_type=DataType.TEXT),
#             Property(name="last_name", data_type=DataType.TEXT),
#             Property(name="brand", data_type=DataType.INT),
#         ],
#     )


# def create_resy_reservations_collection(manager: WeaviateManager):
#     manager.empty_collection(
#         "resyReservations",
#         [
#             Property(name="unit", data_type=DataType.INT),
#             Property(name="block_category", data_type=DataType.INT),
#             Property(name="id_resy_reservations", data_type=DataType.NUMBER),
#             Property(name="time", data_type=DataType.TEXT),
#             Property(name="datetime", data_type=DataType.DATE),
#             Property(name="service", data_type=DataType.TEXT),
#             Property(name="guest", data_type=DataType.TEXT),
#             Property(name="phone", data_type=DataType.TEXT),
#             Property(name="email", data_type=DataType.TEXT),
#             Property(name="party_size", data_type=DataType.INT),
#             Property(name="status", data_type=DataType.TEXT),
#             Property(name="table", data_type=DataType.TEXT),
#             Property(name="visit_note", data_type=DataType.TEXT),
#             Property(name="reserve_number", data_type=DataType.TEXT),
#             Property(name="ai_description", data_type=DataType.TEXT),
#         ],
#         [ReferenceProperty(name="user", target_collection="userProfile")],
#         vectorizer_config=[
#             Configure.NamedVectors.text2vec_openai(
#                 name="ai_description", source_properties=["ai_description"]
#             )
#         ],
#     )


# def create_tock_bookings_collection(manager: WeaviateManager):
#     manager.empty_collection(
#         "tockBookings",
#         [
#             Property(name="unit", data_type=DataType.INT),
#             Property(name="block_category", data_type=DataType.INT),
#             Property(name="id_tock_booking", data_type=DataType.NUMBER),
#             Property(name="time", data_type=DataType.DATE),
#             Property(name="status", data_type=DataType.TEXT),
#             Property(name="tags", data_type=DataType.TEXT),
#             Property(name="postal_code", data_type=DataType.TEXT),
#             Property(name="party_size", data_type=DataType.TEXT),
#             Property(name="booking_owner", data_type=DataType.TEXT),
#             Property(name="experience", data_type=DataType.TEXT),
#             Property(name="price_per_person", data_type=DataType.NUMBER),
#             Property(name="supplements", data_type=DataType.TEXT),
#             Property(name="question_answers", data_type=DataType.TEXT),
#             Property(name="visit_notes", data_type=DataType.TEXT),
#             Property(name="visit_dietary_notes", data_type=DataType.TEXT),
#             Property(name="guest_providede_order_notes", data_type=DataType.TEXT),
#             Property(name="guest_notes", data_type=DataType.TEXT),
#             Property(name="dietary_notes", data_type=DataType.TEXT),
#             Property(name="total_price", data_type=DataType.NUMBER),
#             Property(name="gross_amount_paid", data_type=DataType.NUMBER),
#             Property(name="net_amount_paid", data_type=DataType.NUMBER),
#             Property(name="service_charge", data_type=DataType.NUMBER),
#             Property(name="gratuity", data_type=DataType.NUMBER),
#             Property(name="visits", data_type=DataType.INT),
#             Property(name="tables", data_type=DataType.TEXT),
#             Property(name="servers", data_type=DataType.TEXT),
#             Property(name="booking_method", data_type=DataType.TEXT),
#             Property(name="spouse_name", data_type=DataType.TEXT),
#             Property(name="ai_description", data_type=DataType.TEXT),
#             Property(name="user", data_type=DataType.TEXT),
#         ],
#         vectorizer_config=[
#             Configure.NamedVectors.text2vec_openai(
#                 name="embed_time", source_properties=["time"]
#             )
#         ],
#     )


# # def create_unit_file_collection(manager: WeaviateManager):
# #     manager.create_collection(
# #         "unitFiles",
# #         [
# #             Property(name="unit_id", data_type=DataType.NUMBER),
# #             Property(name="file_url", data_type=DataType.TEXT),
# #             Property(name="file_description", data_type=DataType.TEXT),
# #             Property(name="created_at", data_type=DataType.DATE),
# #             Property(name="updated_at", data_type=DataType.DATE),
# #             Property(name="file_name", data_type=DataType.TEXT),
# #             Property(name="uploaded", data_type=DataType.NUMBER),
# #             Property(name="file_size", data_type=DataType.NUMBER),
# #             Property(name="file_type", data_type=DataType.TEXT),
# #             Property(name="openai_file_id", data_type=DataType.TEXT),
# #         ],
# #     )


# def main():
#     manager = WeaviateManager()

#     if manager.collection_exists("userProfile") is False:
#         create_report_users_collection(manager)

#     # if manager.collection_exists("orders") is False:
#     #     create_orders_collection(manager)

#     if manager.collection_exists("tockBookings") is False:
#         create_tock_bookings_collection(manager)

#     # if manager.collection_exists("resyReservations") is False:
#     #     create_resy_reservations_collection(manager)

#     # if manager.collection_exists("unitFiles") is False:
#     #     create_unitfile_collection(manager)

#     # if manager.collection_exists("unitFileImages") is False:
#     #     create_unitfile_image(manager)


# if __name__ == "django.core.management.commands.shell":
#     main()
