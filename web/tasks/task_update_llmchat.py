from openai import OpenAI
from django.conf import settings
from celery import shared_task
from web.models import LLMChat
import logging

client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)


@shared_task
def task_update_llmchat(thread_id: str, user_id: int | None = None) -> None:
    """
    update llmchat history by pull history from openai when user send a message

    Args:
        thread_id (str): openai thread id
    """
    thread_messages = client.beta.threads.messages.list(
        thread_id=thread_id, order="asc"
    )
    thread_messages_data = thread_messages.data
    logger.info(f"Updating chat history for {thread_id}")

    updated_messages = []
    for message in thread_messages_data:
        role = message.role
        content = message.content[0].text.value

        if role == "user":
            question_start = content.find("User Query:")
            question_end = content.find("Today’s Date:")

            if question_start != -1 and question_end != -1:
                question = content[
                    question_start + len("question:") : question_end
                ].strip()

                message.content[0].text.value = question

        updated_messages.append(message)
    thread_messages.data = updated_messages
    LLMChat.objects.update_or_create(
        thread_id=thread_id,
        defaults={
            "user_id": user_id if user_id else None,
            "messages": thread_messages.json(),
        },
    )
