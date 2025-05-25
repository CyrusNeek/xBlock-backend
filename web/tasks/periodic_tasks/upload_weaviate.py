import datetime
from time import sleep
from celery import shared_task
import logging
from report.models import ToastOrder, TockBooking, ResyReservation, ReportUser
from report.model_fields import REPORT_USER_FIELDS, RESY_RESERVATION_FIELDS, TOAST_ORDER_FIELDS, TOCK_BOOKING_FIELDS
from report.models.guest_profile import Guest, GuestProfile
from web.models import Unit
from django.db.models import Q





logger = logging.getLogger(__name__)


def create_or_update(**kwargs) -> None:
    """
    Create or update an object in the 'userProfile' collection based on 'user_id'.

    :param manager: WeaviateManager instance.
    :param user_data: A dictionary containing the user properties, including 'user_id'.
    :return: The result of the creation or update operation.
    """
    # collection_name, manager, data: dict, field_unique: str = "id"
    collection_name = kwargs.get("collection_name")
    manager = kwargs.get("manager")
    data = kwargs.get("data", {})
    field_unique = kwargs.get("field_unique", "user_id")
    field_id = data.get(field_unique)

    if not field_id:
        raise ValueError(
            f"{collection_name} data must contain '{field_unique}'")

    params = {field_unique: field_id}
    # Step 1: Check if the user with 'user_id' exists
    existing_user_uuid = manager.get_object(collection_name, **params)

    if existing_user_uuid:
        # Step 2: Update the existing user
        logger.info(
            f"{collection_name} with {field_unique} {field_id} exists, updating record...")
        update_result = manager.update_object(
            collection_name, existing_user_uuid, data)
        return update_result
    else:
        # Step 3: Create a new user
        logger.info(
            f"{collection_name} with {field_unique} {field_id} does not exist, creating new record...")
        create_result = manager.create_object(collection_name, data)
        return create_result


def insert_data_to_weaviate_in_chunks(manager, collection_name, data, chunk_size=100, update_function=None, **kwargs):
    """
    A utility function that inserts or updates data into Weaviate in chunks.

    :param manager: WeaviateManager instance.
    :param collection_name: Name of the Weaviate collection.
    :param data: List of data dictionaries to insert or update.
    :param chunk_size: The size of each data chunk to process at once.
    :param update_function: The function to create or update data.
    """
    logger.info(f"INFO: Uploading data to Weaviate. Total: {len(data)} items.")

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]

        # if update_function:
        #     field_unique = kwargs.get("field_unique", "id")
        #     for item in chunk:
        #         update_function(manager=manager, data=item, collection_name=collection_name,
        #                         field_unique=field_unique, field_id=item.get(field_unique))
        # else:
        manager.create_bulk(collection_name, chunk)

        logger.info(f"INFO: Uploaded chunk of {len(chunk)} items to Weaviate.")
        sleep(1)  # Sleep to avoid overwhelming the server


def insert_users_to_weaviate(manager: WeaviateManager, unit: Unit, date: datetime = None) -> None:
    guests = Guest.objects.filter(brand__units__in=[unit]).values_list("pk")

    users = GuestProfile.objects.filter(
        user__in=guests).exclude(toast__isnull=True)
    if date:
        logger.info(f"INFO: Filtering users by reservation date: {date}")
        users = users.filter(reservation_date__gte=date)
    logger.info("-"*20)
    logger.info(f"Query for users: {users.query}")
    logger.info("-"*20)
    if not users.exists():
        logger.info(f"INFO: No users found for the specified unit: {unit}. {users.count()}")
        return

    data = []
    for user in users:

        data.append({
            'user_id': user.pk,
            'email': user.user.email,
            'phone': user.user.phone,
            'first_name': user.user.first_name,
            'last_name': user.user.last_name,
            'brand': user.user.brand.pk,
            'created_at': user.reservation_date,
        })

    insert_data_to_weaviate_in_chunks(
        manager=manager,
        collection_name="userProfile",
        data=data,
        update_function=create_or_update,
        field_unique="user_id"
    )
    users.update(uploaded=True)


def insert_orders_to_weaviate(manager: WeaviateManager, unit: Unit, date: str = None):
    orders = ToastOrder.objects.filter(toast_auth__unit=unit)

    if not orders.exists():
        logger.info("No orders found for the specified unit.")
        return

    if date:
        logger.info(f"INFO: Filtering orders by reservation date: {date}")
        orders = orders.filter(opened__gte=date)

    collection_name = "orders"
    logger.info("-"*20)
    logger.info(f"Query for users: {orders.query}")
    logger.info("-"*20)
    data = []
    for order in orders.values(*TOAST_ORDER_FIELDS):
        data.append({
            "order_id": order['pk'],
            "order_number": order['order_number'],
            "checks": order['checks'],
            "opened": order['opened'].isoformat() if order['opened'] else None,
            "number_of_guests": order['number_of_guests'],
            "tab_names": order['tab_names'],
            "table": order['table'],
            "amount": float(order['amount']),
            "discount_amount": float(order['discount_amount']),
            "service": order['service'],
            "tax": float(order['tax']),
            "tip": float(order['tip']),
            "gratuity": float(order['gratuity'] or 0.00),
            "total": float(order['total']),
            # Add other fields as necessary
        })

    insert_data_to_weaviate_in_chunks(manager, collection_name, data)

    # Mark the orders as uploaded
    orders.update(uploaded=True)


def insert_resy_reservations_to_weaviate(manager: WeaviateManager, unit: Unit, date: str = None):
    reservations = ResyReservation.objects.filter(
        resy_auth__unit=unit)

    if not reservations.exists():
        logger.info("No reservations found for the specified unit.")
        return
    if date:
        logger.info(
            f"INFO: Filtering reservations by reservation date: {date}")
        reservations = reservations.filter(datetime__gte=date)
    collection_name = "resyReservations"
    logger.info("-"*20)
    logger.info(f"Query for users: {reservations.query}")
    logger.info("-"*20)
    data = []
    for reservation in reservations.values(*RESY_RESERVATION_FIELDS):
        date_obj = reservation['datetime'].isoformat(
        ) if reservation['datetime'] else None
        data.append({
            "time": reservation['time'],
            "datetime": date_obj,
            "service": reservation['service'],
            "guest": reservation['guest'],
            "phone": reservation['phone'],
            "email": reservation['email'],
            "party_size": reservation['party_size'] or 0,
            "status": reservation['status'],
            "table": reservation['table'],
            "visit_note": reservation['visit_note'],
            "reserve_number": reservation['reserve_number'],
        })

    insert_data_to_weaviate_in_chunks(manager, collection_name, data)

    # Mark the reservations as uploaded
    reservations.update(uploaded=True)


def insert_tock_bookings_to_weaviate(manager: WeaviateManager, unit: Unit, date: str = None):
    tock_bookings = TockBooking.objects.filter(
        tock__unit__pk=unit.pk)

    if not tock_bookings.exists():
        logger.info("No Tock Bookings found for the specified unit.")
        return
    if date:
        logger.info(
            f"INFO: Filtering Tock Bookings by reservation date: {date}")
        tock_bookings = tock_bookings.filter(time__gte=date)
    collection_name = "tockBookings"
    logger.info("-"*20)
    logger.info(f"Query for users: {tock_bookings.query}")
    logger.info("-"*20)
    data = []
    for booking in tock_bookings.values(*TOCK_BOOKING_FIELDS):
        data.append({
            "time": booking['time'].isoformat() if booking['time'] else None,
            "status": booking['status'],
            "postal_code": booking['postal_code'],
            "party_size": str(booking['party_size']),
            "booking_owner": booking['booking_owner'],
            "experience": booking['experience'],
            "price_per_person": float(booking['price_per_person']),
            "supplements": booking['supplements'],
            "question_answers": booking['question_answers'],
            "visit_notes": booking['visit_notes'],
            "visit_dietary_notes": booking['visit_dietary_notes'],
            "guest_provided_order_notes": booking['guest_provided_order_notes'],
            "guest_notes": booking['guest_notes'],
            "dietary_notes": booking['dietary_notes'],
            "total_price": float(booking['total_price']),
            "gross_amount_paid": float(booking['gross_amount_paid']),
            "net_amount_paid": float(booking['net_amount_paid']),
            "service_charge": float(booking['service_charge'] or 0.00),
            "gratuity": float(booking['gratuity'] or 0.00),
            "visits": booking['visits'],
            "tables": booking['tables'],
            "servers": booking['servers'],
            "booking_method": booking['booking_method'],
            "spouse_name": booking['spouse_name'],
        })

    insert_data_to_weaviate_in_chunks(manager, collection_name, data)

    # Mark the bookings as uploaded
    tock_bookings.update(uploaded=True)

def clear_collection(manager:WeaviateManager):

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
                    Property(name="created_at", data_type=DataType.DATE),

                ],
                [ReferenceProperty(name="user", target_collection="userProfile")],
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_openai(
                        name="embed_time",
                        source_properties=["created_at", "opened"],
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
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_openai(
                        name="embed_time",
                        source_properties=["created_at"],
                    )
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
                    Property(name="created_at", data_type=DataType.DATE),

                ],
                # [ReferenceProperty(name="user", target_collection="userProfile")],
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_openai(
                        name="embed_time",
                        source_properties=["time", "datetime"],
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
                    Property(name="timezone", data_type=DataType.TEXT),
                    Property(name="created_at", data_type=DataType.DATE),

                ],
                references=[ReferenceProperty(name="user", target_collection="userProfile")],
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_openai(
                        name="embed_time",
                        source_properties=["time", "created_at"],
                    )
                ],
            )

    create_orders_collection(manager)
    create_report_users_collection(manager)
    create_resy_reservations_collection(manager)
    create_tock_bookings_collection(manager)

@shared_task
def upload_data_to_weaviate() -> None:
    units = Unit.objects.all()
    manager = WeaviateManager()
    # first clear all collection
    clear_collection(manager)
    for unit in units:
        logger.info(f"INFO: Start uploading data to Weaviate for unit: {unit}")
        today = datetime.date.today()
        today = today - datetime.timedelta(days=2)
        insert_users_to_weaviate(manager, unit, today)
        insert_orders_to_weaviate(manager, unit, today)
        insert_tock_bookings_to_weaviate(manager, unit, today)
        insert_resy_reservations_to_weaviate(manager, unit, today)
