from openai import OpenAI
from django.conf import settings
from celery import shared_task
from report.tasks.periodic.openai_helper import get_or_create_vector_store_id
from roles.permissions import UserPermission
from web.models import UnitFile
import logging
import requests
import os
from django.utils import timezone
from web.models import Assistant
from web.models.block_category import BlockCategory
from web.models.openai_file import OpenAIFile
from web.services.storage_service import StorageService

from roles.constants import (
    UNLIMITED_ACCESS_TO_CONVERSATION_ANALYTICS,
    LIMITED_ACCESS_TO_CONVERSATION_ANALYTICS,
)


client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)


def check_permission(user, block_category=None):
    if block_category == None:
        return True
    if UserPermission.check_user_permission(
        user, UNLIMITED_ACCESS_TO_CONVERSATION_ANALYTICS
    ):
        return True
    elif UserPermission.check_user_permission(
        user, LIMITED_ACCESS_TO_CONVERSATION_ANALYTICS
    ):
        if block_category in BlockCategory.objects.accessible_by_user(user):
            return True
        return False


@shared_task
def task_unit_file_upload_openai(unit_file_id: int) -> None:
    unit_file = UnitFile.objects.get(id=unit_file_id)
    unit = unit_file.unit
    if not unit:
        return

    assistants = Assistant.objects.filter(
        user__in=unit.users.all(), purpose=Assistant.PURPOSE_DEFAULT
    )

    # Generate a unique local filename
    # manager = WeaviateManager()
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    local_filename = f"{unit.name}_{unit_file.file_name}_{timestamp}.pdf"
    # weaviate_file_name = f"{unit.name}_{unit_file.file_name}_{timestamp}.json"

    try:
        url = unit_file.presigned_get_url
        response = requests.get(url)
        response.raise_for_status()

        with open(local_filename, "wb") as f:
            f.write(response.content)

        # if not local_filename.endswith(".pdf"):
        # weaviate_file = TextProcessor.process_pdf(local_filename)

        # with open(weaviate_file_name, "w") as result_file:
        #     json.dump(weaviate_file, result_file)
        #     for idx, text in enumerate(weaviate_file["chunks"]):
        #         if not unit_file.file_name:
        #             unit_file.file_name = unit_file.file_url

        #         manager.create_object(
        #             "unitFile",
        #             {
        #                 "name": unit_file.file_name + " - Chunk " + str(idx),
        #                 "unit": unit.pk,
        #                 "text": text,
        #                 "created_at": timezone.now(),
        #                 "unit_name": unit.name,
        #                 "description": "",
        #             },
        #         )

        # ImageProcessor(manager).process_document(
        #     local_filename, unit.name, unit_file.pk
        # )

        # storage_service.upload_file(weaviate_file_name, "uploads/" + weaviate_file_name)

        with open(local_filename, "rb") as f:
            openai_response = client.files.create(
                file=open(local_filename, "rb"),
                purpose="assistants",
            )

            open_ai_file = OpenAIFile.objects.create(
                file_id=openai_response.id,
                file_name=local_filename,
                unit=unit,
                model_name="unit-file",
                block_category=unit_file.category,
            )

        openai_file_id = openai_response.id
        logger.info(f"Uploaded {unit_file.file_name} to OpenAI: {openai_file_id}")

        # Update the UnitFile instance
        unit_file.openai_file_id = openai_file_id
        unit_file.save()

        for assistant in assistants:
            if not check_permission(assistant.user, unit_file.category):
                continue

            get_or_create_vector_store_id(assistant)
            client.beta.vector_stores.files.create(
                vector_store_id=assistant.vector_store_id, file_id=open_ai_file.file_id
            )

            assistant.files.add(open_ai_file)

            assistant.save()

            # assistant_file = client.beta.assistants.files.create(
            #     assistant_id=asssi, file_id=openai_file_id
            # )
        # logger.info(f"Assistant file created: {assistant_file}")
            logger.info(f"Assistant file created: {assistant.files}")

    except requests.RequestException as e:
        logger.error(f"Error downloading file from storage: {e}")

    except Exception as e:
        logger.error(f"Error processing the file: {e}")

    finally:
        # Remove the downloaded file
        if os.path.exists(local_filename):
            os.remove(local_filename)

    return None
