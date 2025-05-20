import math
from celery import shared_task

from django.utils import timezone
from django.conf import settings

from report.model_fields import REPORT_USER_SERIALIZED_RECORD_SIZE, REPORT_USER_FIELDS
from report.models import (
    ReportUser,
)
from openai import OpenAI
from web.models import Unit, Assistant, OpenAIFile
from django.core.serializers.json import DjangoJSONEncoder
from report.tasks.periodic.openai_helper import get_or_create_vector_store_id, write_chunk

import json

from web.verba_assistant import VerbaAssistant

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def upload_chunk_to_open_ai(chunk, unit_pk, number):
    json_value = json.dumps(
        list(chunk.values("pk", *REPORT_USER_FIELDS)), cls=DjangoJSONEncoder
    )
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(json_value, f"users_{unit_pk}_{timestamp}", number)
    # file_id = client.files.create(
    #     purpose="assistants",
    #     file=open(filename, "rb"),
    # ).id

    file = OpenAIFile.objects.create(
        file_id="-1", file_name=filename,
        unit=Unit.objects.get(pk=unit_pk),
        model_name="users",
    )

    verba = VerbaAssistant()

    verba.upload_document([file])


    return file


@shared_task
def upload_users_openai(unit_pk):
    unit = Unit.objects.get(pk=unit_pk)
    users = ReportUser.objects.filter(brand__units__in=[unit], uploaded=False)
    start = 0
    max_size = math.floor(200 * 1024 * 1024 / REPORT_USER_SERIALIZED_RECORD_SIZE)
    users_len = users.count()

    files: list[OpenAIFile] = []

    assistants = Assistant.objects.filter(
        user__in=unit.users.all(), purpose=Assistant.PURPOSE_DEFAULT
    )

    number = 1
    while start < users_len:
        end = min(users_len, start + max_size)
        users_slice = users[start:end]
        if users_slice.exists() is False:
            break

        files.append(
            upload_chunk_to_open_ai(users_slice, unit_pk, number)
        )

        start = end
        ReportUser.objects.filter(pk__in=users_slice).update(uploaded=True)
        number += 1

    # for assistant in assistants:
    #     get_or_create_vector_store_id(
    #         assistant, unit
    #     )

    #     for file in files:
    #         client.beta.vector_stores.files.create(
    #             vector_store_id=assistant.vector_store_id,
    #             file_id=file.file_id,
    #             metadata={
    #                 "title": f"{file.model_name} of {file.unit}",
    #                 "tag": file.model_name,
    #                 "category": file.block_category,
    #                 "unit": file.unit,
    #                 "date": file.created_at,
    #                 "description": f"This file contains detailed user data for the {file.unit} unit, captured using the {file.model_name} model. The data was collected on {file.created_at}. It includes various user-related metrics and insights specific to the {file.unit}."
    #             }
    #         )

    #         assistant.files.add(file)

    #     assistant.save()

    #     client.beta.assistants.update(
    #         assistant_id=assistant.assistant_id,
    #         tool_resources={"file_search": {
    #             "vector_store_ids": [assistant.vector_store_id]}},
    #     )
