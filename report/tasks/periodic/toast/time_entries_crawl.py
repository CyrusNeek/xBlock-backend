from django.conf import settings
from django.utils import timezone

from .crawler import ToastCrawler, safe_float, get_current_time_format

from report.models import ToastAuth, ToastTimeEntries

from web.services.storage_service import StorageService

from celery import shared_task
import pandas as pd


from datetime import datetime

import time
import os


@shared_task
def crawl_toast_time_entries(toast: ToastAuth, is_initial_triggered, date=None):
    filename = f"tmp-{toast.pk}.pem"

    StorageService().download_file(toast.sshkey.private_key_location, filename)

    result = ToastCrawler(
        host=toast.host,
        username=toast.username,
        location_id=toast.location_id,
        private_key_path=filename,
        date_time=(
            date
            if date != None
            else None if is_initial_triggered is False else get_current_time_format()
        ),
        file_name="TimeEntries.csv",
    ).get_data()

    # os.remove(filename)

    if result.get("error"):
        raise Exception(result.get("error"))

    df = result["result"]

    transactions = df.to_dict(orient="records")

    transaction_instances = []

    for row in transactions:
        transaction_instances.append(
            ToastTimeEntries(
                toast=toast,
                time_entry_id=row["Id"],
                guid=row.get("GUID"),
                employee_id=row["Employee Id"],
                employee_guid=row["Employee GUID"],
                employee_external_id=safe_float(row.get("Employee External Id", None)),
                employee=row["Employee"],
                job_id=row["Job Id"],
                job_guid=row["Job GUID"],
                job_code=safe_float(row["Job Code"]),
                job_title=row["Job Title"],
                in_date=timezone.make_aware(
                    datetime.strptime(row["In Date"], "%m/%d/%y %I:%M %p")
                ),
                out_date=timezone.make_aware(
                    datetime.strptime(row["Out Date"], "%m/%d/%y %I:%M %p")
                ),
                auto_clock_out=row["Auto Clock-out"] == "Yes",
                total_hours=safe_float(row["Total Hours"]),
                unpaid_break_time=safe_float(row["Unpaid Break Time"]),
                paid_break_time=safe_float(row["Paid Break Time"]),
                payable_hours=safe_float(row["Payable Hours"]),
                cash_tips_declared=safe_float(row["Cash Tips Declared"]),
                non_cash_tips=safe_float(row["Non Cash Tips"]),
                total_gratuity=safe_float(row["Total Gratuity"]),
                total_tips=safe_float(row["Total Tips"]),
                tips_withheld=safe_float(row["Tips Withheld"]),
                wage=safe_float(row["Wage"]),
                regular_hours=safe_float(row["Regular Hours"]),
                overtime_hours=safe_float(row["Overtime Hours"]),
                regular_pay=safe_float(row["Regular Pay"]),
                overtime_pay=safe_float(row["Overtime Pay"]),
                total_pay=safe_float(row["Total Pay"]),
            )
        )

    ToastTimeEntries.objects.bulk_create(transaction_instances, ignore_conflicts=True)

    if date == None:
        toast.is_initial_triggered = True
        toast.save()
