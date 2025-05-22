import math
from celery import shared_task

from django.utils import timezone
from django.conf import settings

from report.model_fields import (
    RESY_RESERVATION_SERIALIZED_RECORD_SIZE,
    RESY_RESERVATION_FIELDS,
)
from report.models import (
    ResyReservation,
)
from openai import OpenAI
from report.models.resy_auth import ResyAuth
from web.models import Unit, Assistant
from django.core.serializers.json import DjangoJSONEncoder
from report.tasks.periodic.openai_helper import (
    get_or_create_vector_store_id,
    write_chunk,
)

import json

from web.models.openai_file import OpenAIFile
from web.verba_assistant import VerbaAssistant


client = OpenAI(api_key=settings.OPENAI_API_KEY)



def upload_chunk_to_open_ai(chunk, unit_pk, number, block_category=None):
    json_value = json.dumps(
        list(chunk.values("pk", *RESY_RESERVATION_FIELDS)), cls=DjangoJSONEncoder
    )
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(json_value, f"reservations_{unit_pk}_{timestamp}", number)
    # file_id = client.files.create(
    #     purpose="assistants",
    #     file=open(filename, "rb"),
    # ).id

    file = OpenAIFile.objects.create(
        file_id="-1",
        file_name=filename,
        unit=Unit.objects.get(pk=unit_pk),
        model_name="resy",
        block_category=block_category
    )

    verba = VerbaAssistant()

    verba.upload_document([file])


    return file


@shared_task
def upload_reservations_openai(unit_pk):
    unit = Unit.objects.get(pk=unit_pk)
    reservations = ResyReservation.objects.filter(resy_auth__unit=unit, uploaded=False)
    start = 0
    max_size = math.floor(200 * 1024 * 1024 / RESY_RESERVATION_SERIALIZED_RECORD_SIZE)
    # max_size = float("inf")
    reservations_len = reservations.count()
    assistants = Assistant.objects.filter(
        user__in=unit.users.all(), purpose=Assistant.PURPOSE_DEFAULT
    )
    resy_auth = ResyAuth.objects.filter(unit=unit).first()
    if not resy_auth:
        return
    
    number = 1
    files: list[OpenAIFile] = []

    while start < reservations_len:
        end = min(reservations_len, start + max_size)
        reservations_slice = reservations[start:end]

        if reservations_slice.exists() is False:
            break

        files.append(upload_chunk_to_open_ai(reservations_slice, unit_pk, number, resy_auth.block_category))

        start = end
        ResyReservation.objects.filter(pk__in=reservations_slice).update(uploaded=True)
        number += 1

    # for assistant in assistants:
    #     get_or_create_vector_store_id(assistant, unit)

    #     for file in files:
    #         client.beta.vector_stores.files.create(
    #         vector_store_id=assistant.vector_store_id, file_id=file.file_id,
    #         metadata={
    #             "title": f"{file.model_name} reservations of {file.unit}",
    #             "tag": file.model_name,
    #             "unit": file.unit,
    #             "date": file.created_at,
    #             "description": f"This file contains a comprehensive list of Resy reservations for the {file.unit} unit. The data was generated using the {file.model_name} model and includes all reservation activities recorded on {file.created_at}. This dataset is intended for uploading to OpenAI, providing detailed insights into customer reservation behavior, trends, and unit-specific reservation statistics."
    #         }
    #     )
    #         assistant.files.add(file)

    #     assistant.save()

    #     client.beta.assistants.update(
    #         assistant_id=assistant.assistant_id,
    #         tool_resources={
    #             "file_search": {"vector_store_ids": [assistant.vector_store_id]}
    #         },
    #     )
