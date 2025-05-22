import math
from celery import shared_task

from django.utils import timezone
from django.conf import settings

from report.model_fields import (
    TOAST_ITEM_SELECTION_DETAILS_SERIALIZED_RECORD_SIZE,
    TOAST_ITEM_SELECTION_FIELDS,
)
from report.models import (
    ToastOrder,
    ToastItemSelectionDetails,
)
from openai import OpenAI
from report.models.toast_auth import ToastAuth
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



def upload_chunk_to_open_ai(chunk, unit_pk, number, block_category):
    json_value = json.dumps(
        list(chunk.values("pk", *TOAST_ITEM_SELECTION_FIELDS)), cls=DjangoJSONEncoder
    )
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(json_value, f"toast_items_{unit_pk}_{timestamp}", number)
    # file_id = client.files.create(
    #     purpose="assistants",
    #     file=open(filename, "rb"),
    # ).id

    file = OpenAIFile.objects.create(
        file_id="-1",
        file_name=filename,
        unit=Unit.objects.get(pk=unit_pk),
        model_name="items",
        block_category=block_category
    )

    verba = VerbaAssistant()

    verba.upload_document([file])

    return file


@shared_task
def upload_toast_items_openai(unit_pk):
    unit = Unit.objects.get(pk=unit_pk)
    orders = ToastOrder.objects.filter(toast_auth__unit__pk=unit_pk)
    toast_items = ToastItemSelectionDetails.objects.filter(
        order__in=orders, uploaded=False
    )
    start = 0
    max_size = math.floor(
        200 * 1024 * 1024 / TOAST_ITEM_SELECTION_DETAILS_SERIALIZED_RECORD_SIZE
    )
    # max_size = float("inf")
    toast_items_len = toast_items.count()
    assistants = Assistant.objects.filter(
        user__in=unit.users.all(), purpose=Assistant.PURPOSE_DEFAULT
    )
    toast = ToastAuth.objects.filter(unit=unit).first()
    if not toast: 
        return
    
    number = 1
    files: list[OpenAIFile] = []

    while start < toast_items_len:
        end = min(toast_items_len, start + max_size)
        toast_items_slice = toast_items[start:end]

        if toast_items_slice.exists() is False:
            break

        files.append(upload_chunk_to_open_ai(toast_items_slice, unit_pk, number, toast.block_category))
        start = end
        ToastItemSelectionDetails.objects.filter(pk__in=toast_items_slice).update(
            uploaded=True
        )
        number += 1

    # for assistant in assistants:
    #     get_or_create_vector_store_id(assistant, unit)

    #     for file in files:
    #         client.beta.vector_stores.files.create(
    #             vector_store_id=assistant.vector_store_id, file_id=file.file_id,
    #             metadata={
    #                 "title": f"{file.model_name} items of {file.unit}",
    #                 "tag": file.model_name,
    #                 "unit": file.unit,
    #                 "date": file.created_at,
    #                 "description": f"This file contains a detailed list of Toast items for the {file.unit} unit, generated using the {file.model_name} model. The data was collected on {file.created_at} and is intended for uploading to OpenAI. It includes comprehensive information on each Toast item, facilitating efficient processing and analysis within the OpenAI environment."
    #             }
    #         )
    #         assistant.files.add(file)

    #     assistant.save()

    #     client.beta.assistants.update(
    #         assistant_id=assistant.assistant_id,
    #         tool_resources={
    #             "file_search": {"vector_store_ids": [assistant.vector_store_id]}
    #         },
    #     )
