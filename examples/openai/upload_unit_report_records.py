from report.tasks.periodic.upload_orders_open_ai import upload_orders_openai
from report.tasks.periodic.upload_payments_open_ai import upload_payments_openai
from report.tasks.periodic.upload_toast_items_open_ai import upload_toast_items_openai
from report.tasks.periodic.upload_reservations_open_ai import upload_reservations_openai
from report.tasks.periodic.upload_users_open_ai import upload_users_openai

from web.tasks.task_meeting import upload_meeting_to_openai, upload_tasks_to_openai
from web.models import Unit, Meeting, Task
from report.models import (
    ToastOrder,
    ReportUser,
    ToastItemSelectionDetails,
    ResyReservation,
    ToastPayment,
    TockBooking,
)


def main():
    units = Unit.objects.all()
    ToastOrder.objects.update(uploaded=False)
    ToastItemSelectionDetails.objects.update(uploaded=False)
    ResyReservation.objects.update(uploaded=False)
    ToastPayment.objects.update(uploaded=False)
    TockBooking.objects.update(uploaded=False)
    ReportUser.objects.update(uploaded=False)

    for unit in units:
        upload_orders_openai(unit.pk)
        upload_payments_openai(unit.pk)
        upload_reservations_openai(unit.pk)
        upload_toast_items_openai(unit.pk)
        upload_users_openai(unit.pk)

        meetings = Meeting.objects.filter(unit=unit)

        for meeting in meetings:
            # upload_meeting_to_openai(
            #     meeting.diarization,
            #     meeting.pk,
            #     meeting.name,
            #     create_or_retrieve_vector_store(meeting.unit, "global").id,
            # )
            tasks = list(
                meeting.tasks.values(
                    "assignee",
                    "status",
                    "created_at",
                    "description",
                    "meeting",
                    "unit",
                    "due_date",
                )
            )
            upload_tasks_to_openai(
                tasks,
                meeting.id,
                meeting.name,
            )


if __name__ == "django.core.management.commands.shell":
    main()