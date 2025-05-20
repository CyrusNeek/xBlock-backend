from report.models.tock_auth import TockAuth
from report.models.tock_booking import TockBooking
from roles.constants import LIMITED_BLOCK_ACCESS, UNLIMITED_BLOCK_ACCESS
from web.models.user import User
from web.views.openai.tools.utils import (
    queryset_columns_to_string,
    queryset_values_list_to_string,
)
from web.models import (
    Reservation,
    Unit,
)  # Assuming Unit model is relevant for filtering by address
from roles.permissions import UserPermission
from datetime import datetime
from typing import List, Optional
import logging
import copy
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json


logger = logging.getLogger(__name__)

formatted_date = datetime.now().strftime("%b %d %Y")

MODEL = "Reservation"
FUNCTION_NAME = "reservation_assistant_function"
KNOWLEDGE_RETURN_RECORD_LIMIT = 100
FIELDS = [
    "first_name",
    "last_name",
    "reservation_time",
    "reservation_date",
    "experience",
    "tags",
    "notes",
    "email",
    "phone_number",
]
EMPTY_KNOWLEDGE = f"Query result: No matched {MODEL} found from database."


TOCK_BOOKING_FIELDS = [
    "report_triggered_at",
    "time",
    "status",
    "postal_code",
    "party_size",
    "booking_owner",
    "experience",
    "price_per_person",
    "supplements",
    "question_answers",
    "visit_notes",
    "visit_dietary_notes",
    "guest_provided_order_notes",
    "guest_notes",
    "dietary_notes",
    "total_price",
    "gross_amount_paid",
    "net_amount_paid",
    "service_charge",
    "gratuity",
    "confirmation",
    "visits",
    "last_visit_date",
    "last_visit_time",
    "group_visits",
    "last_group_visit_date",
    "last_group_visit_time",
    "last_group_visit_restaurant",
    "spouse_name",
    "birthday",
    "booking_method",
    "modified_by",
    "final_status",
    "tables",
    "servers",
    "dining_time_seconds",
]


RESERVATION_TOOL = {
    "type": "function",
    "function": {
        "name": FUNCTION_NAME,
        "description": "Get reservation details for a restaurant unit based on date",
        "parameters": {
            "type": "object",
            "properties": {
                "unit_address": {
                    "type": "string",
                    "description": "Unit/Restaurant name and address pair for the Tock report. Ask for clarification and provide a list of available address pairs if user did not specify one.",
                },
                "date": {
                    "type": "string",
                    "description": "Filter reservations by the reservation date.",
                },
            },
            "required": ["unit_address", "date"],
        },
    },
}


def get_dynamic_reservation_tool(user: User) -> dict:
    dynamic_reservation_tool = copy.deepcopy(RESERVATION_TOOL)

    # Modify the copied dictionary to include unit addresses associated with the user
    unit_address_enum = [
        unit.name + " -- " + unit.address
        for unit in user.all_units
        if unit.address != ""
    ]
    dynamic_reservation_tool["function"]["parameters"]["properties"]["unit_address"][
        "enum"
    ] = unit_address_enum

    logger.info(
        f"Dynamic Update Reservation Tool unit_address arg enum: {unit_address_enum}"
    )
    return dynamic_reservation_tool


def reservation_assistant_function(
    user: User,
    unit_address: str,
    date: str,
):
    # TODO: refactor permissions and
    #  Quick book models based on the new implementations on reports and roles
    #  module

    # required_permission = [
    #     # "tock_admin", "tock_manager"
    # ]

    # Access check
    # if not UserPermission.check_user_permission(user, required_permission):
    #     return "You do not have permission to access this QuickBooks report."

    if UserPermission.check_user_permission(user, [UNLIMITED_BLOCK_ACCESS]):
        accessible_tock_auths = TockAuth.objects.filter(
            unit=user.all_owned_brands.values_list("unit").flat(2)
        )

    elif UserPermission.check_user_permission(user, [LIMITED_BLOCK_ACCESS]):
        accessible_tock_auths = TockAuth.objects.filter(unit=user.all_units)

    else:
        accessible_tock_auths = TockAuth.objects.none()

    bookings = TockBooking.objects.filter(
        tock__in=accessible_tock_auths,
        time__date=date,
        tock__unit__address__icontains=unit_address.split(" -- ")[0],
    )

    if bookings.exists():
        bookings = bookings[:KNOWLEDGE_RETURN_RECORD_LIMIT]

        # Convert to a dictionary
        bookings_data = list(bookings.values(*TOCK_BOOKING_FIELDS))

        # Combine all data
        combined_data = {"bookings": bookings_data}

        # Convert to JSON
        knowledge = json.dumps(combined_data, cls=DjangoJSONEncoder)

        # Log the combined data
        logger.info(f"knowledge: {knowledge}")
        return knowledge

    return EMPTY_KNOWLEDGE
