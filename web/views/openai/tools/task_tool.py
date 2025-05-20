from web.models.user import User
from web.views.openai.tools.utils import (
    queryset_columns_to_string,
    queryset_values_list_to_string,
)
from ....models import Task
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

formatted_date = datetime.now().strftime("%b %d %Y")

STATUS_TYPES = [i[0] for i in Task.Status.choices]
FUNCTION_NAME = "task_assistant_function"
SORT_BY = ["created_at", "due_date", "-created_at", "-due_date"]
STATUS_TYPES = ["Backlog", "Todo", "In Progress", "Done", "Calceled"]
KNOWLEDGE_COLUMNS = [
    "assignee",
    "description",
    "created_by__first_name",
    "due_date",
    "created_at",
    "meeting__name",
]
KNOWLEDGE_RECORD_LIMIT = 30
MODEL = "Task"
EMPTY_KNOWLEDGE = f"Query result: No matched {MODEL} found from database."

TASK_TOOL = {
    "type": "function",
    "function": {
        "name": FUNCTION_NAME,
        "description": "Get information about tasks in user's unit.",
        "parameters": {
            "type": "object",
            "properties": {
                "sort_by": {
                    "type": "string",
                    "enum": SORT_BY,
                    "description": "Sort tasks by created_at or due_date",
                },
                "created_date_from": {
                    "type": "string",
                    "description": f"Today is {formatted_date}. Return python date string refer to start period from user's query on task created_at date",
                },
                "created_date_to": {
                    "type": "string",
                    "description": f"Today is {formatted_date}. Return python date string refer to end period from user's query on task created_at date",
                },
                "due_date_from": {
                    "type": "string",
                    "description": f"Today is {formatted_date}. Return python date string refer to start period from user's query on task due date",
                },
                "due_date_to": {
                    "type": "string",
                    "description": f"Today is {formatted_date}. Return python date string refer to end period from user's query on task due date",
                },
            },
        },
    },
}


def task_assistant_function(
    user: User,
    sort_by: Optional[str] = None,
    created_date_from: Optional[str] = None,
    created_date_to: Optional[str] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None,
):  
    # Query tasks from OpenAI function calling arguments
    tasks = Task.objects.accessible_by_user(user)

    if sort_by:
        tasks = tasks.order_by(sort_by)
    if created_date_from:
        tasks = tasks.filter(created_at__gte=created_date_from)
    if created_date_to:
        tasks = tasks.filter(created_at__lte=created_date_to)
    if due_date_from:
        tasks = tasks.filter(due_date__gte=due_date_from)
    if due_date_to:
        tasks = tasks.filter(due_date__lte=due_date_to)
    if tasks.exists():
        # convert queryset columns and data to string as assistant's knowledge
        tasks = tasks[:KNOWLEDGE_RECORD_LIMIT]
        tasks_values_list = tasks.values_list(*KNOWLEDGE_COLUMNS)
        tasks_table_string = queryset_values_list_to_string(tasks_values_list)
        tasks_column_string = queryset_columns_to_string(KNOWLEDGE_COLUMNS, MODEL)
        knowledge = tasks_column_string + tasks_table_string
        logging.info("Task Tool Knowledge" + knowledge)
        return knowledge

    return EMPTY_KNOWLEDGE
