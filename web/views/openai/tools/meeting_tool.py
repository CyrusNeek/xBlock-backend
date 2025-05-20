from web.models.user import User
from web.views.openai.tools.utils import (
    queryset_columns_to_string,
    queryset_values_list_to_string,
)
from web.models import Meeting
from datetime import datetime
from typing import List, Optional
import logging
from constance import config

logger = logging.getLogger(__name__)

formatted_date = datetime.now().strftime("%b %d %Y")

MODEL = "Meeting"
FUNCTION_NAME = "meeting_assistant_function"
KNOWLEDGE_RETURN_RECORD_LIMIT = 30
STATUS_TYPES = ["Backlog", "Todo", "In Progress", "Done", "Calceled"]
FIELDS = ["summary", "length", "name", "created_by__first_name", "created_at", "unit"]
EMPTY_KNOWLEDGE = f"Query result: No matched {MODEL} found from database."


MEETING_TOOL = {
    "type": "function",
    "function": {
        "name": FUNCTION_NAME,
        "description": config.MEETING_TOOL_DESC,
        "parameters": {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "description": config.MEETING_TOOL_ARG_FIELDS_DESC,
                    "items": {
                        "type": "string",
                        "enum": FIELDS,
                    },
                },
                "participants_filter": {
                    "type": "array",
                    "description": config.MEETING_TOOL_ARG_PARTICIPANTS_FILTER_DESC,
                    "items": {
                        "type": "string",
                    },
                },
                "created_by": {
                    "type": "string",
                    "description": config.MEETING_TOOL_ARG_CREATED_BY_DESC,
                },
                "created_date_from": {
                    "type": "string",
                    "description": f"Today is {formatted_date}"
                    + config.MEETING_TOOL_ARG_CREATED_DATE_FROM_DESC,
                },
                "created_date_to": {
                    "type": "string",
                    "description": f"Today is {formatted_date}"
                    + config.MEETING_TOOL_ARG_CREATED_DATE_TO_DESC,
                },
            },
            "required": ["fields"],
        },
    },
}


def meeting_assistant_function(
    user: User,
    fields: List[str],
    participants_filter: Optional[List[str]] = [],
    created_by: Optional[str] = None,
    created_date_from: Optional[str] = None,
    created_date_to: Optional[str] = None,
):
    # Query meetings from OpenAI function calling arguments
    meetings = Meeting.objects.accessible_by_user(user)
    meetings = (
        meetings.only(*fields)
        .order_by("-created_at")
    )

    # Filter by participants' first names
    if participants_filter:
        for first_name in participants_filter:
            meetings = meetings.filter(participants__first_name__iexact=first_name)

    if created_date_from:
        meetings = meetings.filter(created_at__gte=created_date_from)
    if created_date_to:
        meetings = meetings.filter(created_at__lte=created_date_to)
    if created_by:
        meetings = meetings.filter(created_by__first_name__iexact=created_by)
    if meetings.exists():
        # convert queryset columns and data to string as assistant's knowledge
        meetings = meetings[:KNOWLEDGE_RETURN_RECORD_LIMIT]
        meetings_values_list = meetings.values_list(*fields)
        meetings_table_string = queryset_values_list_to_string(meetings_values_list)
        meetings_column_string = queryset_columns_to_string(fields, MODEL)
        knowledge = meetings_column_string + meetings_table_string
        logger.info(f"{meetings.count()} {MODEL} included.")
        logging.info(knowledge)
        return knowledge

    return EMPTY_KNOWLEDGE
