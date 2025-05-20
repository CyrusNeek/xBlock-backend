from django.conf import settings

from .crawler import ToastCrawler, get_current_time_format, input_format
from .modifiers_selection_details import crawl_toast_modifiers_selection_details

from report.models import ToastAuth, ToastOrder, ToastItemSelectionDetails
from report.tasks.periodic.upload_toast_items_open_ai import upload_toast_items_openai

from web.services.storage_service import StorageService
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError


from datetime import datetime

import os


def safe_id(value):
    if str(value).endswith(".0"):
        return str(value).replace(".0", "")

    return str(value)


@shared_task(max_retries=3, default_retry_delay=10)
def crawl_toast_item_selection_details(
    toast: ToastAuth, is_initial_triggered, date=None
):
    try:
        filename = f"tmp-{toast.pk}.pem"

        StorageService().download_file(toast.sshkey.private_key_location, filename)

        result = ToastCrawler(
            host=toast.host,
            username=toast.username,
            location_id=toast.location_id,
            private_key_path=filename,
            date_time=(
                date
                if date is not None
                else (
                    None if is_initial_triggered is False else get_current_time_format()
                )
            ),
            file_name="ItemSelectionDetails.csv",
        ).get_data()

        df = result["result"]

        transactions = df.to_dict(orient="records")

        transaction_instances = []

        for transaction in transactions:
            try:
                sent_date = datetime.strptime(transaction["Sent Date"], input_format)
                order_date = datetime.strptime(transaction["Order Date"], input_format)

                order = ToastOrder.objects.get(
                    order_id=safe_id(transaction["Order Id"])
                )

                transaction_instances.append(
                    ToastItemSelectionDetails(
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
                        item_id=transaction["Item Id"],
                        master_id=transaction["Master Id"],
                        sku=transaction.get("SKU", ""),
                        plu=transaction.get("PLU", ""),
                        menu_item=transaction.get("Menu Item", ""),
                        menu_subgroups=transaction.get("Menu Subgroup(s)", ""),
                        menu_group=transaction.get("Menu Group", ""),
                        menu=transaction.get("Menu", ""),
                        sales_category=transaction.get("Sales Category", ""),
                        gross_price=transaction["Gross Price"],
                        discount=transaction["Discount"],
                        net_price=transaction["Net Price"],
                        quantity=transaction["Qty"],
                        tax=round(transaction["Tax"], 2),
                        void=transaction["Void?"],
                        deferred=transaction["Deferred"],
                        tax_exempt=transaction["Tax Exempt"],
                        tax_inclusion_option=transaction.get(
                            "Tax Inclusion Option", ""
                        ),
                        dining_option_tax=transaction.get("Dining Option Tax", ""),
                        tab_name=transaction.get("Tab Name", ""),
                    )
                )
            except Exception as e:
                print(f"Error processing transaction: {transaction}")
                # raise e

        ToastItemSelectionDetails.objects.bulk_create(
            transaction_instances, ignore_conflicts=True
        )

        crawl_toast_modifiers_selection_details.delay(
            toast, toast.is_initial_triggered, date
        )
        upload_toast_items_openai.delay(toast.unit.pk)

    except MaxRetriesExceededError:
        print(
            f"Error crawling item selection details for {toast.pk}: max retries exceeded"
        )
        raise
    except Exception as e:
        print(f"Error crawling item selection details for {toast.pk}: {e}")
        raise e
