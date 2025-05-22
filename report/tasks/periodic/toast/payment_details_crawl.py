from .crawler import ToastCrawler, safe_float, parse_date, get_current_time_format
from .cash_entries_crawl import crawl_toast_cash_entries
from report.models import ToastAuth, ToastOrder, ReportUser, ToastPayment
from report.tasks.periodic.upload_payments_open_ai import upload_payments_openai
from web.services.storage_service import StorageService
from celery import shared_task
from django.db import transaction
import logging
import pandas as pd
from datetime import datetime
import os


# Initialize the logger for tracking events
logger = logging.getLogger(__name__)


# Helper function to generate the SSH filename with date and time for traceability
def generate_filename(toast):
    """
    Generate an SSH filename with current date and time for the given ToastAuth instance.
    Args:
        toast (ToastAuth): The ToastAuth instance.
    Returns:
        str: Generated filename with the current timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"tmp-{toast.pk}-{timestamp}.pem"


@shared_task
def crawl_toast_payment_details(toast_pk: int, is_initial_triggered, date=None):
    """
    Crawls payment details from the Toast service, processes the records, and inserts them into the database.
    Args:
        toast (ToastAuth): The ToastAuth instance.
        is_initial_triggered (bool): Flag indicating whether this is the first trigger.
        date (str): Optional date for fetching specific day data.
    """
    try:
        toast = ToastAuth.objects.get(pk=toast_pk)
    except ToastAuth.DoesNotExist:
        logger.error(f"ToastAuth not found for PK: {toast_pk}")
        return
    # Generate a timestamped filename for the SSH key
    filename = generate_filename(toast)

    try:
        # Download the SSH key from the storage
        StorageService().download_file(toast.sshkey.private_key_location, filename)

        # Initialize the ToastCrawler to fetch payment details
        result = ToastCrawler(
            host=toast.host,
            username=toast.username,
            location_id=toast.location_id,
            private_key_path=filename,
            date_time=date if date else (None if not is_initial_triggered else get_current_time_format()),
            file_name="PaymentDetails.csv",
        ).get_data()

        df = result["result"]
        transactions = df.to_dict(orient="records")

        transaction_instances = []

        # Begin processing each transaction
        for row in transactions:
            paid_date = parse_date(row["Paid Date"])
            order_date = parse_date(row["Order Date"])
            refund_date = parse_date(row["Refund Date"], "%m/%d/%Y %I:%M %p") if pd.notnull(row["Refund Date"]) else None
            void_date = parse_date(row["Void Date"], "%m/%d/%Y %I:%M %p") if pd.notnull(row["Void Date"]) else None

            # Find the order associated with this payment
            try:
                order = ToastOrder.objects.get(order_id=row["Order Id"])
            except ToastOrder.DoesNotExist:
                logger.error(f"Order not found for Order Id: {row['Order Id']}")
                continue

            # Find or create a ReportUser instance for this transaction
            report_user = ReportUser.objects.create_safe(
                row["Email"], row["Phone"], toast.unit.brand
            )

            # Prepare the payment instance for bulk insert
            transaction_instances.append(
                ToastPayment(
                    payment_id=row["Payment Id"],
                    order=order,
                    paid_date=paid_date,
                    order_date=order_date,
                    check_id=row["Check Id"],
                    check_number=row["Check #"],
                    tab_name=row["Tab Name"] if pd.notnull(row["Tab Name"]) else None,
                    server=row["Server"] if pd.notnull(row["Server"]) else None,
                    table=row["Table"] if pd.notnull(row["Table"]) else None,
                    dining_area=row["Dining Area"] if pd.notnull(row["Dining Area"]) else None,
                    service=row["Service"] if pd.notnull(row["Service"]) else None,
                    dining_option=row["Dining Option"] if pd.notnull(row["Dining Option"]) else None,
                    house_account=row["House Acct #"] if pd.notnull(row["House Acct #"]) else None,
                    amount=safe_float(row["Amount"]),
                    tip=safe_float(row["Tip"]),
                    gratuity=safe_float(row["Gratuity"]),
                    total=safe_float(row["Total"]),
                    swiped_card_amount=safe_float(row["Swiped Card Amount"]),
                    keyed_card_amount=safe_float(row["Keyed Card Amount"]),
                    amount_tendered=safe_float(row["Amount Tendered"]),
                    refunded=row["Refunded"] if pd.notnull(row["Refunded"]) else None,
                    refund_date=refund_date,
                    refund_amount=safe_float(row["Refund Amount"]),
                    refund_tip_amount=safe_float(row["Refund Tip Amount"]),
                    void_user=row["Void User"] if pd.notnull(row["Void User"]) else None,
                    void_approver=row["Void Approver"] if pd.notnull(row["Void Approver"]) else None,
                    void_date=void_date,
                    status=row["Status"],
                    type=row["Type"],
                    cash_drawer=row["Cash Drawer"] if pd.notnull(row["Cash Drawer"]) else None,
                    card_type=row["Card Type"] if pd.notnull(row["Card Type"]) else None,
                    other_type=row["Other Type"] if pd.notnull(row["Other Type"]) else None,
                    user=report_user,
                    last_4_card_digits=row["Last 4 Card Digits"] if pd.notnull(row["Last 4 Card Digits"]) else None,
                    vmcd_fees=safe_float(row["V/MC/D Fees"]),
                    room_info=row["Room Info"] if pd.notnull(row.get("Room Info")) else None,
                    receipt=row["Receipt"] if pd.notnull(row["Receipt"]) else None,
                    source=row["Source"],
                )
            )

        # Perform a bulk insert for the payment instances
        with transaction.atomic():
            ToastPayment.objects.bulk_create(transaction_instances, ignore_conflicts=True)

        # Trigger the next task for crawling cash entries and uploading payment data
        # crawl_toast_cash_entries.delay(toast, is_initial_triggered, date)
        upload_payments_openai.delay(toast.unit.pk)

        logger.info(f"Successfully processed {len(transaction_instances)} payment records for ToastAuth: {toast.pk}")

    except Exception as e:
        logger.error(f"Error processing payment details for ToastAuth: {toast.pk}, Error: {e}")
        toast.status = ToastAuth.FAIL
        toast.error_detail = str(e)
        toast.save()

    finally:
        # Clean up the downloaded SSH key file if it exists
        if os.path.exists(filename):
            os.remove(filename)
