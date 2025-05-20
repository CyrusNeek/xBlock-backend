import logging
import json
from datetime import datetime, timedelta
from django.utils import timezone
from openai import OpenAI
from report.models import GuestProfile, ResyReservation, TockBooking
from web.models import User, Unit, BlockCategory
from roles.permissions import UserPermission
from roles.constants import UNLIMITED_ANSWER_ACCESS, LIMITED_ANSWER_ACCESS
from django.conf import settings
from django.db.models import Q, Sum
from django.db.models.query import QuerySet
from celery import shared_task

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@shared_task(bind=True, max_retries=5, default_retry_delay=5)
def openai_filtering_agent(self, user_query):
    try:
        prompt = f"""
            You are a JSON generator specifically designed for a restaurant reservation system. Your role is to analyze user queries related to reservations and generate a JSON object containing the relevant properties based on the query's intent. You only include properties that are explicitly mentioned or implied in the user's query. Do not include any explanatory text, markdown formatting, or any other characters besides the JSON itself. Output *only* the JSON.
            
            ### System Instructions:
            
            1. **Analyze the user's query:**
            - Identify the key entities and relationships mentioned in the query, such as dates, names, table numbers, guest properties (e.g., lifetime value, allergies), and specific requests.
            - Determine whether the query is asking for multiple objects (plural) or a single object (singular). Add the `plural_question` property to indicate this distinction:
                - Set `plural_question` to `true` if the query references multiple objects or a count (e.g., "How many reservations do we have today?").
                - Set `plural_question` to `false` if the query references a single object or is singular in nature (e.g., "Who is sitting at Table 7?").
            
            2. **Map entities to JSON properties:**
            Use the following mapping to create the JSON object:
            
            - “first_name”: The first name of the person who made the reservation.
            - “last_name”: The last name of the person who made the reservation.
            - “reservation_date”: The date for which the reservation is made.
            - “lifetime_value”: A value representing the guest’s spending history or loyalty level with the restaurant.
            - “booking_owner”: The person who owns or manages the booking. (Often internal use)
            - “guest_notes”: Special notes about the guest, including preferences or personalized details.
            - “confirmation”: Information about the reservation confirmation, which could be a unique code or link.
            - “tables”: The table(s) reserved by the user.
            - “birthday”: Date of birth of the user who made the reservation.
            - “service”: The service requested by the user for booking (e.g., bar, lunch, dinner).
            - “guest”: General guest information (structure not defined in this prompt).
            - “status”: The current status of the reservation (e.g., confirmed, cancelled, pending).
            - “time”: The reserved time for the restaurant.
            - “party_size”: The number of guests in the user's party.
            - “visit_note”: Specific notes for this particular reservation (e.g., "birthday celebration").
            - “allergy_tags”: Registered allergies for the user.
            - “guest_tags”: Tags associated with the booking user (e.g., VIP, regular).
            - “total_visits”: The total number of times the user has visited the restaurant.
            - “special_requests”: Special requests registered by the user for the booking.
            - **“plural_question”**: A Boolean property set to `true` if the query refers to multiple objects, and `false` if it refers to a single object.
            
            3. **Handle implicit queries:**
            - Queries about existence (e.g., "Are there any allergy tags for...?") should set the corresponding property to true.
            - Queries about maximum/minimum should use ">>" for maximum and "<<" for minimum as the value.
            - Queries with comparison operators (>, <) should include the operator and the value in the JSON value string (e.g., ">10", "<500").
            - Queries related to time must strictly follow these rules:
                    - The value of the time property must be either:
                        - An exact time in the format hh:mm:ss.
                        - A Boolean (true or false) if the query is about the presence or absence of time information.
                    - Do not include comparison operators (>>, <<, <, or >). If such operators are implied in the query, omit the time property entirely.
            - **Ensure that `plural_question` is correctly set based on whether the query asks about multiple entities or not.**
            
            4. **Output Format:**
            Output a valid JSON object with only the relevant properties filled based on the user's query. Do not include null properties.
            
            ### Input/Output Examples:
            
            Input: What is the largest reservation group size for today?
            Output:
            {{"reservation_date": "2024-11-02", "party_size": ">>", "plural_question": false}}

            Input: What is the total number of guests expected today?
            Output:
            {{"reservation_date": "2024-11-02", "plural_question": true}}

            Input: Who is the guest at table 22?
            Output:
            {{"tables": "22", "plural_question": false}}

            Input: How many reservations do we have today?
            Output:
            {{"plural_question": true}}

            Input: What time is Table 10 booked?
            Output:
            {{"tables": "10", "plural_question": true}}

            Input: What reservations are assigned to Table 5 today?
            Output:
            {{"reservation_date": "2024-11-02", "tables": "5", "plural_question": true}}

            Input: What special request did Stephanie Kim make?
            Output:
            {{"first_name": "Stephanie", "last_name": "Kim", "special_requests": true, "plural_question": false}}

            Input: What time is Table 3 booked for today?
            Output:
            {{'reservation_date': '2024-11-22', 'tables': '3', 'plural_question': true}}

            Input: what is the first reservation of today ??
            Output:
            {{'reservation_date': '2024-11-22', 'time': true, 'plural_question': false}}

            Now, generate the JSON output for the following user query:
            Today’s Date: {datetime.now().date()}
            User Query: {user_query}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0,
        )
        response = json.loads(response.choices[0].message.content)
        if response == {} or len(response) == 1 and "plural_question" in response:
            return {}

        if "reservation_date" not in response:
            response["reservation_date"] = timezone.now().strftime("%Y-%m-%d")
        # response["start_date"] = datetime.now().strftime("%Y-%m-%d")
        # response["end_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        print(response)
        return response
    except Exception as e:
        logger.error("Error in openai_agent: %s", e)
        raise


def construct_filters(filter_data):
    filters = Q()
    suffixes = ["__iexact", "__icontains"]
    try:
        for key, value in filter_data.items():
            if (
                isinstance(value, str)
                and value.startswith(">")
                and not value.startswith(">>")
            ):
                filters &= Q(**{f"{key}__gte": value[1:].strip()})
            elif (
                isinstance(value, str)
                and value.startswith("<")
                and not value.startswith("<<")
            ):
                filters &= Q(**{f"{key}__lte": value[1:].strip()})
            elif isinstance(value, str) and key in ("reservation_date", "birthday"):
                if key == "birthday":
                    filters &= Q(**{key: datetime.strptime(value, "%Y-%m-%d").date()})
                else:
                    filters &= Q(
                        **{f"{key}__date": datetime.strptime(value, "%Y-%m-%d").date()}
                    )
            elif value is True and not any(key.endswith(suffix) for suffix in suffixes):
                filters &= Q(**{f"{key}__isnull": False})
            elif value is False and not any(
                key.endswith(suffix) for suffix in suffixes
            ):
                filters &= Q(**{f"{key}__isnull": True})
            elif value == "<<" or value == ">>":
                continue
            else:
                filters &= Q(**{key: value})
        return filters
    except Exception as e:
        logger.error("Error in construct_filters: %s", e)
        raise


def filter_and_order_data(data, filter_data):
    try:

        data = data.filter(construct_filters(filter_data))
        for key, value in filter_data.items():
            if isinstance(value, str) and value == ">>":
                return data.order_by(f"-{key}").first()
            elif isinstance(value, str) and value == "<<":
                return data.order_by(key).first()
        return data
    except Exception as e:
        logger.error("Error in filter_and_order_data: %s", e)
        raise


@shared_task(bind=True, max_retries=5, default_retry_delay=5)
def filter_openai_response_objects(self, text, user_id):
    try:
        # Fetch user and related data
        user = User.objects.get(pk=user_id)
        user_access_units = user_units_check(user_id)
        user_access_block_category = user_block_category_check(user_id)
        user_brand_owner = user.affiliation

        filter_data = openai_filtering_agent(text)
        guest_filter_json = get_filtering_json(filter_data, "guest")
        resy_filter_json = get_filtering_json(filter_data, "resy")
        tock_filter_json = get_filtering_json(filter_data, "tock")

        # Time-based filtering
        current_date = timezone.now().date()
        start_time = timezone.now() - timedelta(minutes=30)
        end_of_day = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)

        date_filter = {"reservation_date__date": current_date} if "today" in text.lower() else {
            "reservation_date__range": (start_time, end_of_day)
        }

        # Fetch guest data
        guest_data = (
            GuestProfile.objects.select_related("user")
            .filter(user__brand__owner=user_brand_owner, **date_filter)
            .order_by("reservation_date")
        )
        guest_data = filter_and_order_data(guest_data, guest_filter_json)

        # Handle Resy and Tock data
        resy_data, tock_data = [], []
        if isinstance(guest_data, QuerySet):
            resy_data = guest_data.filter(model_name="Resy")
            tock_data = guest_data.filter(model_name="Tock")
        elif guest_data:
            if guest_data.model_name == "Resy":
                resy_data = [guest_data]
            elif guest_data.model_name == "Tock":
                tock_data = [guest_data]

        resy_objects = resy_data.values_list("object_id", flat=True) if resy_data else []
        tock_objects = tock_data.values_list("object_id", flat=True) if tock_data else []

        # Fetch filtered bookings
        permissions = {
            "UNLIMITED": Q(pk__in=tock_objects) & Q(tock__unit__in=user_access_units),
            "LIMITED": Q(pk__in=tock_objects)
            & Q(tock__unit__in=user_access_units)
            & Q(tock__block_category__in=user_access_block_category),
        }
        if UserPermission.check_user_permission(user, UNLIMITED_ANSWER_ACCESS):
            tock_filtered = TockBooking.objects.filter(permissions["UNLIMITED"])
            resy_filtered = ResyReservation.objects.filter(
                Q(pk__in=resy_objects) & Q(resy_auth__unit__in=user_access_units) & Q(datetime__date=current_date)
            )
        elif UserPermission.check_user_permission(user, LIMITED_ANSWER_ACCESS):
            tock_filtered = TockBooking.objects.filter(permissions["LIMITED"])
            resy_filtered = ResyReservation.objects.filter(
                Q(pk__in=resy_objects)
                & Q(resy_auth__unit__in=user_access_units)
                & Q(datetime__date=current_date)
                & Q(resy_auth__block_category__in=user_access_block_category)
            )
        else:
            return {}

        # Process final data
        final_tock = filter_and_order_data(tock_filtered, tock_filter_json)
        final_resy = filter_and_order_data(resy_filtered, resy_filter_json)

        tock_final_ids = list(final_tock.values_list("pk", flat=True)) if isinstance(final_tock, QuerySet) else [final_tock.pk]
        resy_final_ids = list(final_resy.values_list("pk", flat=True)) if isinstance(final_resy, QuerySet) else [final_resy.pk]

        objects = GuestProfile.objects.filter(
            object_id__in=resy_final_ids + tock_final_ids
        ).order_by("reservation_date")

        if not objects.exists():
            return {
                "reservation_count": 0,
                "guests_count": 0,
                "reserved_tables": [],
                "reservation_detail": {},
            }

        # Build context
        if filter_data.get("plural_question"):
            contexts = [build_context(obj) for obj in objects]
        else:
            first_object = objects.first()
            contexts = [build_context(first_object)]
            return {
                "reservation_count": 1,
                "guests_count": calculate_guests_number(first_object, user_access_units),
                "reserved_tables": get_reservation_tables(first_object, user_access_units),
                "reservation_detail": contexts,
            }

        return {
            "reservation_count": objects.count(),
            "guests_count": calculate_guests_number(objects, user_access_units),
            "reserved_tables": get_reservation_tables(objects, user_access_units),
            "reservation_detail": contexts,
        }

    except Exception as e:
        logger.error("Error in filter_guest_profile_objects: %s", e)
        raise



def get_filtering_json(original_json, model_name):
    try:
        fields_by_model = {
            "guest": {
                "reservation_date",
                # "start_date",
                # "end_date",
                "first_name",
                "last_name",
                "lifetime_value",
                "total_visits",
            },
            "tock": {
                "booking_owner",
                "party_size",
                "status",
                "guest_notes",
                "confirmation",
                "guest_tags",
                "tables",
                "birthday",
                "visits",
            },
            "resy": {
                "service",
                "guest",
                "status",
                "time",
                "party_size",
                "visit_note",
                "table",
                "allergy_tags",
                "guest_tags",
                "special_requests",
                "guest_notes",
            },
        }

        filtered_json = {}
        string_keys = {
            "first_name",
            "last_name",
            "booking_owner",
            "status",
            "service",
        }

        for key in fields_by_model.get(model_name, []):
            if model_name == "guest" and key in {
                "first_name",
                "last_name",
                "lifetime_value",
                "total_visits",
            }:
                if key in original_json:
                    if key == "lifetime_value":
                        filtered_json[f"user__Lifetime_value"] = original_json[key]
                    else:
                        filtered_json[f"user__{key}"] = original_json[key]
            elif key in original_json:
                filtered_json[key] = original_json[key]

        if model_name == "resy" and "tables" in original_json:
            filtered_json["table"] = original_json["tables"]

        if model_name == "tock" and "guest_tags" in original_json:
            filtered_json["guest_tags__name"] = original_json["guest_tags"]

        keys_to_modify = [
            key for key in filtered_json if key in string_keys or key == "time"
        ]

        for key in keys_to_modify:
            if key in string_keys:
                filtered_json[f"{key}__iexact"] = filtered_json.pop(key)
            elif key == "time":
                filtered_json[f"{key}__icontains"] = filtered_json.pop(key)

        return filtered_json
    except Exception as e:
        logger.error("Error in get_filtering_json: %s", e)
        raise


def build_context(guest_profile):
    context = {
        "reservation_date": guest_profile.reservation_date,
        "phone": guest_profile.user.phone,
        "email": guest_profile.user.email,
        "first_name": guest_profile.user.first_name,
        "last_name": guest_profile.user.last_name,
        "lifetime_value": guest_profile.user.Lifetime_value,
        "total_visits": guest_profile.user.total_visits,
        "occupied": find_occupied_tables(guest_profile.pk),
    }
    if guest_profile.model_name == GuestProfile.TOCK:
        context.update(get_tock_booking_context(guest_profile))
    elif guest_profile.model_name == GuestProfile.RESY:
        context.update(get_resy_reservation_context(guest_profile))
    return context


def get_tock_booking_context(guest_profile):
    try:
        data_object = TockBooking.objects.get(pk=guest_profile.object_id)

        return {
            "booking_owner": data_object.booking_owner,
            "party_size": data_object.party_size,
            "status": data_object.status,
            "guest_notes": data_object.guest_notes,
            "guest_tags": data_object.guest_tags,
            # "visits": data_object.visits,
            "tables": data_object.tables,
            "confirmation": data_object.confirmation,
            "brand": data_object.brand,
            "servers": data_object.servers,
            "birthday": data_object.birthday,
        }
    except TockBooking.DoesNotExist:
        return {}


def get_resy_reservation_context(guest_profile):
    try:
        data_object = ResyReservation.objects.get(pk=guest_profile.object_id)
        return {
            "guest": data_object.guest,
            "party_size": data_object.party_size,
            "status": data_object.status,
            "guest_notes": data_object.guest_notes,
            "guest_tags": data_object.guest_tags,
            # "total_visits": data_object.total_visits,
            "tables": data_object.table,
            "service": data_object.service,
            "time": data_object.time,
            "visit_note": data_object.visit_note,
            "allergy_tags": data_object.allergy_tags,
            "special_requests": data_object.special_requests,
            "ticket_type": data_object.ticket_type,
        }
    except TockBooking.DoesNotExist:
        return {}


def find_occupied_tables(guest_profile_id):
    guest_profile = GuestProfile.objects.get(pk=guest_profile_id)
    reservation_time = guest_profile.reservation_date

    try:
        current_time = timezone.now()
        start_time = reservation_time - timedelta(minutes=15)
        end_time = reservation_time + timedelta(minutes=45)

        if start_time <= current_time <= end_time:
            return True
        else:
            return False
    except Exception as e:
        logger.error(
            f"Failed to calculate start and end time for {guest_profile}, Error: {e}"
        )
        return False


def user_units_check(user_id):
    try:
        user = User.objects.get(pk=user_id)

        if UserPermission.check_user_permission(user, UNLIMITED_ANSWER_ACCESS):
            return set(
                Unit.objects.filter(brand__owner=user.affiliation).values_list(
                    "pk", flat=True
                )
            )

        elif UserPermission.check_user_permission(user, LIMITED_ANSWER_ACCESS):
            return set(user.units.all().values_list("pk", flat=True))

    except User.DoesNotExist:
        logger.error("Error to check user permission")
        return []


def user_block_category_check(user_id):
    try:
        user = User.objects.get(pk=user_id)
        return BlockCategory.objects.accessible_by_user(user)

    except User.DoesNotExist:
        logger.error("Error to check user permission")
        return []


def calculate_guests_number(query, user_units):
    current_date = timezone.now()

    if hasattr(query, 'filter'):
        resy_data = query.filter(model_name="Resy")
        resy_objects = (
            list(resy_data.values_list("object_id", flat=True)) if resy_data else []
        )
    else:
        logger.error("Query object is not a valid queryset")
        return 0

    resy = ResyReservation.objects.filter(
        Q(pk__in=resy_objects)
        & Q(resy_auth__unit__in=user_units)
        & Q(datetime__date=current_date)
    ).aggregate(total=Sum("party_size"))

    return resy["total"] or 0



def get_reservation_tables(query, user_units):
    current_date = timezone.now()

    if hasattr(query, 'filter'):
        resy_data = query.filter(model_name="Resy")
        resy_objects = (
            list(resy_data.values_list("object_id", flat=True)) if resy_data else []
        )
    else:
        logger.error("Query object is not a valid queryset")
        return []

    resy = ResyReservation.objects.filter(
        Q(pk__in=resy_objects)
        & Q(resy_auth__unit__in=user_units)
        & Q(datetime__date=current_date)
    )

    reserved_tables = []
    for reservation in resy:
        reserved_tables.extend(reservation.table.split(","))

    return list(set(reserved_tables))
