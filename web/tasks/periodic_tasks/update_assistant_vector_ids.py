from web.models import Assistant, Unit
from openai import OpenAI
from django.conf import settings
from datetime import datetime


client = OpenAI(api_key=settings.OPENAI_API_KEY)


# DEPRECATED
def update_assistant_vectors(assistant: Assistant):
    # units: list[Unit] = Unit.objects.accessible_by_user(assistant.user)

    # accessible_vector_ids = []
    # formatted_date = datetime.now().strftime("%b %d %Y")

    # unit_names = ",".join([Unit.name for Unit in units])

    # for unit in units:
    #     accessible_vector_ids.extend(
    #         [
    #             unit.vector_id,
    #             unit.users_vector_id,
    #             unit.resy_rating_vector_id,
    #             unit.resy_reservation_vector_id,
    #             unit.order_vector_id,
    #             unit.order_items_vector_id,
    #             unit.toast_payment_vector_id,
    #             unit.toast_item_selection_vector_id,
    #             unit.toast_check_vector_id
    #         ]
    #     )

    # client.beta.assistants.update(
    #     assistant.assistant_id,
    #     tools=[{"type": "file_search"},],
    #     instructions=f"You are an assistant for {unit_names} staff. You have access to their internal documents, financial report from QuickBooks, meeting data, and task data. Help {unit_names} employee with your knowledge base. Today's date time is {formatted_date}.",

    #     tool_resources={"file_search": {
    #         "vector_store_ids": [accessible_vector_ids]}}
    # )
    pass


def add_file_id_to_assistant(assistant: Assistant, file_id: str):
    client.beta.vector_stores.files.create(
        vector_store_id=assistant.vector_store_id, file_id=file_id
    )
