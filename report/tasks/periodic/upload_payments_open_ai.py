import math
from celery import shared_task

from django.utils import timezone
from django.conf import settings

from report.model_fields import (
    TOAST_PAYMENT_SERIALIZED_RECORD_SIZE,
    TOAST_PAYMENT_FIELDS,
)
from report.models import ToastPayment, ToastOrder, ToastAuth
from openai import OpenAI
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
        list(chunk.values("pk", *TOAST_PAYMENT_FIELDS)), cls=DjangoJSONEncoder
    )
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(json_value, f"payments_{unit_pk}_{timestamp}", number)
    # file_id = client.files.create(
    #     purpose="assistants",
    #     file=open(filename, "rb"),
    # ).id

    verba = VerbaAssistant()


    file = OpenAIFile.objects.create(
        file_id="-1",
        file_name=filename,
        unit=Unit.objects.get(pk=unit_pk),
        model_name="payments",
        block_category=block_category
    )

    verba.upload_document([file])

    return file


@shared_task
def upload_payments_openai(unit_pk):
    unit = Unit.objects.get(pk=unit_pk)
    orders = ToastOrder.objects.filter(toast_auth__unit__pk=unit_pk)
    payments = ToastPayment.objects.filter(order__in=orders, uploaded=False)
    toast_auth = ToastAuth.objects.filter(unit=unit).first()
    if not toast_auth:
        return
    start = 0
    max_size = math.floor(200 * 1024 * 1024 / TOAST_PAYMENT_SERIALIZED_RECORD_SIZE)
    # max_size = float("inf")
    payments_len = payments.count()
    assistants = Assistant.objects.filter(
        user__in=unit.users.all(), purpose=Assistant.PURPOSE_DEFAULT
    )
    number = 1
    files: list[OpenAIFile] = []

    while start < payments_len:
        end = min(payments_len, start + max_size)
        payments_slice = payments[start:end]

        if payments_slice.exists() is False:
            break

        files.append(upload_chunk_to_open_ai(payments_slice, unit_pk, number, toast_auth.block_category))
        start = end
        ToastPayment.objects.filter(pk__in=payments_slice).update(uploaded=True)
        number += 1

    # for assistant in assistants:
    #     # get_or_create_vector_store_id(assistant, unit)

    #     for file in files:
    #         # client.beta.vector_stores.files.create(
    #         #     vector_store_id=assistant.vector_store_id, file_id=file.file_id,
    #         #     metadata={
    #         #         "title": f"{file.model_name} payments of {file.unit}",
    #         #         "tag": file.model_name,
    #         #         "unit": file.unit,
    #         #         "date": file.created_at,
    #         #         "description": f"This file contains a comprehensive dataset of payments for the {file.unit} unit, generated using the {file.model_name} model. The data, collected on {file.created_at}, includes receipts and bills. This dataset is intended for uploading to OpenAI, providing detailed insights into payment transactions, billing patterns, and unit-specific financial activities."
    #         #     }
    #         # )
    #         assistant.files.add(file)

    #     assistant.save()

    #     # client.beta.assistants.update(
    #     #     assistant_id=assistant.assistant_id,
    #     #     tool_resources={
    #     #         "file_search": {"vector_store_ids": [assistant.vector_store_id]}
    #     #     },
    #     # )
