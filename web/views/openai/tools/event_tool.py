from web.models.user import User
from web.views.openai.tools.utils import (
    queryset_columns_to_string,
    queryset_values_list_to_string,
)
from report.models import Event
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

formatted_date = datetime.now().strftime("%b %d %Y")

FUNCTION_NAME = "event_assistant_function"
KNOWLEDGE_COLUMNS = [
    "name",
    "link",
    "date",
]
KNOWLEDGE_RECORD_LIMIT = 10
MODEL = "Event"
EMPTY_KNOWLEDGE = f"Query result: No matched {MODEL} found from database."

EVENT_TOOL = {
    "type": "function",
    "function": {
        "name": FUNCTION_NAME,
        "description": "Get information about upcoming events.",
    },
}


def event_assistant_function(
    user: User,
):  
    logger.info("Executing event_assistant_function")
    events = Event.objects.all()[:10]  # Adjust the queryset as necessary
    if events.exists():
        # convert queryset columns and data to string as assistant's knowledge
        events = events[:KNOWLEDGE_RECORD_LIMIT]
        events_values_list = events.values_list(*KNOWLEDGE_COLUMNS)
        events_table_string = queryset_values_list_to_string(events_values_list)
        events_column_string = queryset_columns_to_string(KNOWLEDGE_COLUMNS, MODEL)
        knowledge = events_column_string + events_table_string
        logging.info("Event Tool Knowledge" + knowledge)
        return knowledge

    return EMPTY_KNOWLEDGE
