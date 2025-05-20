import math
from celery import shared_task

from django.utils import timezone
from django.conf import settings

from report.model_fields import (
    TOAST_ITEM_SELECTION_DETAILS_SERIALIZED_RECORD_SIZE,
    TOAST_ITEM_SELECTION_FIELDS,
    TOCK_BOOKING_FIELDS
)
from report.models import ToastOrder, ToastItemSelectionDetails, TockBooking
from openai import OpenAI
from report.models.tock_auth import TockAuth
from web.models import Unit, Assistant
from django.core.serializers.json import DjangoJSONEncoder
from report.tasks.periodic.openai_helper import (
    create_or_retrieve_vector_store,
    get_or_create_vector_store_id,
    write_chunk,
)

import json

from web.models.openai_file import OpenAIFile
from web.verba_assistant import VerbaAssistant

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def upload_chunk_to_open_ai(chunk, unit_pk, number, block_category=None):
    json_value = json.dumps(
        list(chunk.values("pk", *TOCK_BOOKING_FIELDS)), cls=DjangoJSONEncoder
    )
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = write_chunk(json_value, f"tock_bookings_{unit_pk}_{timestamp}", number)
    # file_id = client.files.create(
    #     purpose="assistants",
    #     file=open(filename, "rb"),
    # ).id

    file = OpenAIFile.objects.create(
        file_id="-1",
        file_name=filename,
        unit=Unit.objects.get(unit_pk),
        model_name="tock",
        block_category=block_category
    )

    verba = VerbaAssistant()

    verba.upload_document([file])

    return file


@shared_task
def upload_tockbookings_openai(unit_pk):
    unit = Unit.objects.get(pk=unit_pk)
    tockbookings = TockBooking.objects.filter(tock__unit__pk=unit_pk, uploaded=False)
    start = 0
    max_size = math.floor(
        200 * 1024 * 1024 / TOAST_ITEM_SELECTION_DETAILS_SERIALIZED_RECORD_SIZE
    )
    tock = TockAuth.objects.filter(unit=unit).first()
    if not tock:
        return
    tock_bookings_len = tockbookings.count()
    # vector_store_id = create_or_retrieve_vector_store(
    #     unit, ""
    # ).id
    # assistants = Assistant.objects.filter(
    #     user__in=unit.users.all(), purpose=Assistant.PURPOSE_DEFAULT
    # )
    number = 1
    files: list[OpenAIFile] = []

    while start < tock_bookings_len:
        end = min(tock_bookings_len, start + max_size)
        toast_items_slice = tockbookings[start:end]

        if toast_items_slice.exists() is False:
            break

        files.append(upload_chunk_to_open_ai(toast_items_slice, unit_pk, number, tock.block_category))
        start = end
        TockBooking.objects.filter(pk__in=toast_items_slice).update(
            uploaded=True
        )
        number += 1

    # for assistant in assistants:
    #     get_or_create_vector_store_id(assistant, unit)

    #     for file in files:
    #         client.beta.vector_stores.files.create(
    #             vector_store_id=assistant.vector_store_id,
    #             file_id=file.file_id,
    #             metadata={
    #                 "title": f"{file.model_name} bookings of {file.unit}",
    #                 "tag": file.model_name,
    #                 "unit": file.unit,
    #                 "date": file.created_at,
    #                 "description": f"This file contains detailed booking data for the {file.unit} unit, recorded using the {file.model_name} model. The data encompasses all Tock bookings made on {file.created_at}, providing insights into reservation patterns, user preferences, and booking frequencies specific to the {file.unit}."
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
