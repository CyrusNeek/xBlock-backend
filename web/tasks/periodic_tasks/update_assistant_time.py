from openai import OpenAI
from django.conf import settings
from celery import shared_task
import logging
from datetime import datetime
from report.tasks.periodic.openai_helper import get_or_create_vector_store_id
from web.models import Assistant, Unit
from web.models.openai_file import OpenAIFile
from web.tasks.unit_file.task_unitfile_creation import check_permission

client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)


@shared_task
def task_update_assistant_instruction() -> None:
    """
    update assistant instruction with today's date
    """
    formatted_date = datetime.now().strftime("%b %d %Y")
    logger.info(f"Updating assistant instructions with date: {formatted_date}")

    assistants = Assistant.objects.filter(purpose=Assistant.PURPOSE_DEFAULT)

    for assistant in assistants:
        logger.info(f"Updating assistant {assistant.assistant_id}")

        files = OpenAIFile.objects.filter(
            unit__in=Unit.objects.accessible_by_user(assistant.user)
        )

        get_or_create_vector_store_id(assistant)

        for file in files:
            #FIXME: ensure about the permission and the statement
            if not check_permission(assistant.user, file.block_category):
                continue
            try:

                client.beta.vector_stores.files.create(
                    vector_store_id=assistant.vector_store_id, file_id=file.file_id
                )
                assistant.files.add(file)
            except Exception:
                pass

        assistant.save()
