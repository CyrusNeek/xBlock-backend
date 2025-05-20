import math
from celery import shared_task

from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from report.model_fields import (
    TOAST_ORDER_FIELDS,
    TOAST_ORDER_SERIALIZED_RECORD_SIZE,
)
from report.models import (
    ToastOrder, ToastAuth
)
from openai import OpenAI
from web.models import Unit, Assistant
from django.core.serializers.json import DjangoJSONEncoder
from report.tasks.periodic.openai_helper import (
    get_or_create_vector_store_id,
    write_chunk,
)

import json
import os

from web.models.openai_file import OpenAIFile
from web.verba_assistant import VerbaAssistant

client = OpenAI(api_key=settings.OPENAI_API_KEY)


ORDERS_FIELDS = TOAST_ORDER_FIELDS


def upload_chunk_to_open_ai(chunk, unit_pk, number, block_category=None):
    json_value = json.dumps(
        list(chunk.values("pk", *ORDERS_FIELDS)), cls=DjangoJSONEncoder
    )
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(json_value, f"orders_{unit_pk}_{timestamp}", number)
    verba = VerbaAssistant()


    # file_id = client.files.create(
    #     purpose="assistants",
    #     file=open(filename, "rb"),
    # ).id
    

    file = OpenAIFile.objects.create(
        file_id="-1",
        file_name=filename,
        unit=Unit.objects.get(pk=unit_pk),
        model_name="orders",
        block_category=block_category
    )

    verba.upload_document([file])

    return file

@shared_task
def upload_orders_openai(unit_pk):
    unit = Unit.objects.get(pk=unit_pk)
    orders = ToastOrder.objects.filter(~Q(user=None)).filter(toast_auth__unit=unit, uploaded=False)
    toast_auth = ToastAuth.objects.filter(unit=unit).first()

    if not toast_auth:
        return
    
    start = 0
    max_size = math.floor(200 * 1024 * 1024 / TOAST_ORDER_SERIALIZED_RECORD_SIZE)
    # max_size = float("inf")

    orders_len = orders.count()
    # assistants = Assistant.objects.filter(
    #     user__in=unit.users.all(), purpose=Assistant.PURPOSE_DEFAULT
    # )
    number = 1

    files = []

    while start < orders_len:
        end = min(orders_len, start + max_size)
        orders_slice = orders[start:end]
        if orders_slice.exists() is False:
            break
        files.append(upload_chunk_to_open_ai(orders_slice, unit_pk, number, toast_auth.block_category))
        start = end
        ToastOrder.objects.filter(pk__in=orders_slice).update(uploaded=True)
        number += 1

    # for assistant in assistants:
    #     # get_or_create_vector_store_id(assistant, unit)

    #     for file in files:
    #         client.beta.vector_stores.files.create(
    #             vector_store_id=assistant.vector_store_id,
    #             file_id=file.file_id,
    #             metadata={
    #                 "title": f"{file.model_name} of {file.unit}",
    #                 "tag": file.model_name,
    #                 "unit": file.unit,
    #                 "date": file.created_at,
    #                 "description": f"This file contains a detailed dataset of customer orders for the {file.unit} unit, generated using the {file.model_name} model. The data was collected on {file.created_at} and includes all orders placed by customers while at the restaurant. This dataset is intended for uploading to OpenAI, providing insights into customer preferences, ordering patterns, and unit-specific sales data."
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
