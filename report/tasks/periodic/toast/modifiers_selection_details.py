from django.conf import settings
from django.utils import timezone

from .crawler import ToastCrawler, safe_float, get_current_time_format, input_format
from .time_entries_crawl import crawl_toast_time_entries

from report.models import ToastAuth, ToastOrder, ToastModifiersSelectionDetails
from web.services.storage_service import StorageService

from celery import shared_task


from datetime import datetime

import os


@shared_task
def crawl_toast_modifiers_selection_details(
    toast: ToastAuth, is_initial_triggered, date=None
):
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
        file_name="ModifiersSelectionDetails.csv",
    ).get_data()

    df = result["result"]

    # os.remove(filename)

    transactions = df.to_dict(orient="records")

    transaction_instances = []

    for transaction in transactions:
        sent_date = datetime.strptime(transaction["Sent Date"], input_format)
        order_date = datetime.strptime(transaction["Order Date"], input_format)

        order = ToastOrder.objects.get(order_id=transaction["Order Id"])

        transaction_instances.append(
            ToastModifiersSelectionDetails(
                toast=toast,
                order=order,
                sent_date=sent_date,
                order_date=order_date,
                check_id=transaction["Check Id"],
                server=transaction.get("Server", ""),
                table=transaction.get("Table", ""),
                dining_area=transaction.get("Dining Area", ""),
                service=transaction.get("Service", ""),
                dining_option=transaction.get("Dining Option", ""),
                item_selection_id=transaction["Item Selection Id"],
                modifier_id=transaction["Modifier Id"],
                master_id=transaction["Master Id"],
                modifier_sku=transaction.get("Modifier SKU", ""),
                modifier_plu=transaction.get("Modifier PLU", ""),
                modifier=transaction.get("Modifier", ""),
                option_group_id=transaction["Option Group ID"],
                option_group_name=transaction.get("Option Group Name", ""),
                parent_menu_selection_item_id=transaction[
                    "Parent Menu Selection Item ID"
                ],
                parent_menu_selection=transaction.get("Parent Menu Selection", ""),
                sales_category=transaction.get("Sales Category", ""),
                gross_price=transaction["Gross Price"],
                discount=transaction["Discount"],
                net_price=transaction["Net Price"],
                quantity=transaction["Qty"],
                void=transaction["Void?"],
                void_reason_id=transaction.get("Void Reason ID", ""),
                void_reason=transaction.get("Void Reason", ""),
            )
        )

    ToastModifiersSelectionDetails.objects.bulk_create(
        transaction_instances, ignore_conflicts=True
    )

    crawl_toast_time_entries.delay(toast, toast.is_initial_triggered)
