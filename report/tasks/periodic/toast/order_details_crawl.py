from report.utils import log_to_analytic_report
from .crawler import ToastCrawler, get_current_time_format, input_format
from .payment_details_crawl import crawl_toast_payment_details
from report.models import ToastAuth, ToastOrder
from web.services.storage_service import StorageService
from celery import shared_task, chain
from report.tasks.periodic.upload_orders_open_ai import upload_orders_openai
from datetime import datetime
from django.db import transaction
import pandas as pd
import logging


# Initialize logger for logging important events and debugging information
logger = logging.getLogger(__name__)


# Helper function to generate filename with date and time
def generate_filename(toast, suffix):
    """
    Generates a filename with the current date and time for traceability.
    Args:
        toast (ToastAuth): The ToastAuth instance.
        suffix (str): The file suffix (e.g., '.pem').
    Returns:
        str: Generated filename.
    """
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"tmp-{toast.pk}-{current_time}{suffix}"


# Helper function to download SSH private key and return the filename
def download_ssh_key(toast):
    """
    Downloads the SSH private key for the ToastAuth instance and saves it with a timestamp in the filename.
    Args:
        toast (ToastAuth): The authentication object containing SSH key details.
    Returns:
        str: The file path of the downloaded key.
    """
    filename = generate_filename(toast, ".pem")
    StorageService().download_file(toast.sshkey.private_key_location, filename)
    return filename


# Task to handle crawling and processing Toast data after the last cron job
@shared_task
def after_last_cronjob(*args, pk, dates):
    """
    After the final cronjob is done, this task processes payment details.
    Args:
        pk (int): Primary key of the ToastAuth object.
        dates (list): List of dates to process.
    """
    toast = ToastAuth.objects.get(pk=pk)
    for date in dates:
        # crawl_toast_payment_details(toast, False, date)
        crawl_toast_payment_details.delay(toast.pk, False, date)


# Task to handle crawling and processing Toast order details
@shared_task
def crawl_toast_order_details(toast_pk: int, is_initial_triggered: bool):
    """
    Crawls Toast order details and processes them into the database.
    Args:
        toast (ToastAuth): The ToastAuth instance.
        is_initial_triggered (bool): Indicates if this is an initial trigger or a recurring one.
    """
    try:
        toast = ToastAuth.objects.get(pk=toast_pk)
    except ToastAuth.DoesNotExist:
        return

    filename = download_ssh_key(toast)

    # Initial trigger: Fetch historical data
    if not toast.is_initial_triggered:
        try:
            # Get list of dates for historical data
            dates = ToastCrawler(
                host=toast.host,
                username=toast.username,
                location_id=toast.location_id,
                private_key_path=filename,
                date_time=None,
                file_name="OrderDetails.csv",
            ).get_history()["list"]

            date_array = sorted(dates, key=int)

            # Schedule cronjobs for all but the last date
            for date in date_array[:-1]:
                logger.info(f"Scheduling cronjob for date: {date}")
                crawl_toast_order_detail_by_date.delay(toast.pk, date)

            # Schedule the last cronjob and chain it with after_last_cronjob
            last_cronjob = crawl_toast_order_detail_by_date.s(
                toast.pk, date_array[-1])
            # last_cronjob = crawl_toast_order_detail_by_date(
            #     toast, date_array[-1]) # For test
            task_chain = chain(
                last_cronjob,
                after_last_cronjob.s(pk=toast.pk, dates=date_array),
            )
            logger.info(
                f"Scheduling task chain for last date: {date_array[-1]}")
            task_chain.delay()

            # Update toast status and save
            toast.status = ToastAuth.VERIFIED
            toast.is_initial_triggered = True
            toast.save()
        except Exception as e:
            logger.error(f"Error during initial trigger: {e}")
            toast.status = ToastAuth.FAIL
            toast.error_detail = str(e)
            log_to_analytic_report(
                model_name="TOAST", status=False, error_detail=str(e), unit=toast.unit)
        return

    # Regular trigger: Fetch the most recent data
    try:
        result = ToastCrawler(
            host=toast.host,
            username=toast.username,
            location_id=toast.location_id,
            private_key_path=filename,
            date_time=get_current_time_format() if toast.is_initial_triggered else None,
            file_name="OrderDetails.csv",
        ).get_data()
    except Exception as e:
        logger.error(f"Error fetching Toast data: {e}")
        toast.status = ToastAuth.FAIL
        toast.error_detail = str(e)
        toast.save()
        log_to_analytic_report(
            model_name="TOAST", status=False, error_detail=str(e), unit=toast.unit)
        raise e

    # If the result indicates failure, log and raise an exception
    if not result["status"]:
        toast.status = ToastAuth.FAIL
        toast.error_detail = str(result["error"] if "error" in result else "")
        toast.save()
        log_to_analytic_report(
            model_name="TOAST", status=False, error_detail=str(result["error"]), unit=toast.unit)
        raise Exception(result["error"])

    # Process and save the transactions
    process_transactions(result["result"], toast)

    # Trigger payment details crawling after order details are processed
    crawl_toast_payment_details.delay(toast.pk, is_initial_triggered)


# Helper function to process and save transactions into the database


def process_transactions(data_frame, toast):
    """
    Processes a pandas DataFrame of transactions and saves them to the database.
    If a transaction with the same order_id already exists, it is updated.
    Otherwise, a new transaction is inserted.

    Args:
        data_frame (pd.DataFrame): The DataFrame containing transaction data.
        toast (ToastAuth): The ToastAuth instance associated with the transactions.
    """
    logger.info(f"Processing transactions for toast pk: {toast.pk}")
    transactions = data_frame.to_dict(orient="records")
    order_ids = [transaction["Order Id"] for transaction in transactions]

    # Fetch existing transactions with the same order IDs
    existing_orders = ToastOrder.objects.filter(order_id__in=order_ids)
    existing_orders_dict = {order.order_id: order for order in existing_orders}

    new_instances = []
    updated_instances = []
    logger.info("-"*10)
    logger.info(f"Processing {len(transactions)} transactions.")
    logger.info(
        f"new instances: {len(new_instances)} and existing instances: {len(existing_orders_dict)}")
    logger.info("-"*10)

    try:
        for transaction_item in transactions:
            opened_date = datetime.strptime(
                transaction_item["Opened"], input_format)
            paid_date = datetime.strptime(transaction_item["Paid"], input_format) if pd.notnull(
                transaction_item["Paid"]) else None
            closed_date = datetime.strptime(transaction_item["Closed"], input_format) if pd.notnull(
                transaction_item["Closed"]) else None

            order_id = transaction_item["Order Id"]
            if str(order_id) in existing_orders_dict:
                # Update existing order
                existing_order = existing_orders_dict[str(order_id)]
                existing_order.order_number = int(transaction_item["Order #"])
                existing_order.checks = transaction_item["Checks"]
                existing_order.opened = opened_date
                existing_order.number_of_guests = int(
                    transaction_item["# of Guests"])
                existing_order.tab_names = transaction_item["Tab Names"] if pd.notnull(
                    transaction_item["Tab Names"]) else None
                existing_order.server = transaction_item["Server"] if pd.notnull(
                    transaction_item["Server"]) else None
                existing_order.table = transaction_item["Table"] if pd.notnull(
                    transaction_item["Table"]) else None
                existing_order.revenue_center = transaction_item["Revenue Center"] if pd.notnull(
                    transaction_item["Revenue Center"]) else None
                existing_order.dining_area = transaction_item["Dining Area"] if pd.notnull(
                    transaction_item["Dining Area"]) else None
                existing_order.service = transaction_item["Service"] if pd.notnull(
                    transaction_item["Service"]) else None
                existing_order.dining_options = transaction_item["Dining Options"] if pd.notnull(
                    transaction_item["Dining Options"]) else None
                existing_order.discount_amount = float(transaction_item["Discount Amount"]) if pd.notnull(
                    transaction_item["Discount Amount"]) else None
                existing_order.amount = float(transaction_item["Amount"]) if pd.notnull(
                    transaction_item["Amount"]) else None
                existing_order.tax = float(transaction_item["Tax"]) if pd.notnull(
                    transaction_item["Tax"]) else None
                existing_order.tip = float(transaction_item["Tip"]) if pd.notnull(
                    transaction_item["Tip"]) else None
                existing_order.gratuity = float(transaction_item["Gratuity"]) if pd.notnull(
                    transaction_item["Gratuity"]) else None
                existing_order.total = float(transaction_item["Total"]) if pd.notnull(
                    transaction_item["Total"]) else None
                existing_order.voided = bool(transaction_item["Voided"]) if pd.notnull(
                    transaction_item["Voided"]) else False
                existing_order.paid = paid_date
                existing_order.closed = closed_date
                existing_order.duration_opened_to_paid = transaction_item["Duration (Opened to Paid)"] if pd.notnull(
                    transaction_item["Duration (Opened to Paid)"]) else None
                existing_order.order_source = transaction_item["Order Source"] if pd.notnull(
                    transaction_item["Order Source"]) else None
                updated_instances.append(existing_order)
            else:
                # Create new order
                new_instances.append(
                    ToastOrder(
                        toast_auth=toast,
                        order_id=str(order_id),
                        order_number=int(transaction_item["Order #"]),
                        checks=transaction_item["Checks"],
                        opened=opened_date,
                        number_of_guests=int(transaction_item["# of Guests"]),
                        tab_names=transaction_item["Tab Names"] if pd.notnull(
                            transaction_item["Tab Names"]) else None,
                        server=transaction_item["Server"] if pd.notnull(
                            transaction_item["Server"]) else None,
                        table=transaction_item["Table"] if pd.notnull(
                            transaction_item["Table"]) else None,
                        revenue_center=transaction_item["Revenue Center"] if pd.notnull(
                            transaction_item["Revenue Center"]) else None,
                        dining_area=transaction_item["Dining Area"] if pd.notnull(
                            transaction_item["Dining Area"]) else None,
                        service=transaction_item["Service"] if pd.notnull(
                            transaction_item["Service"]) else None,
                        dining_options=transaction_item["Dining Options"] if pd.notnull(
                            transaction_item["Dining Options"]) else None,
                        discount_amount=float(transaction_item["Discount Amount"]) if pd.notnull(
                            transaction_item["Discount Amount"]) else None,
                        amount=float(transaction_item["Amount"]) if pd.notnull(
                            transaction_item["Amount"]) else None,
                        tax=float(transaction_item["Tax"]) if pd.notnull(
                            transaction_item["Tax"]) else None,
                        tip=float(transaction_item["Tip"]) if pd.notnull(
                            transaction_item["Tip"]) else None,
                        gratuity=float(transaction_item["Gratuity"]) if pd.notnull(
                            transaction_item["Gratuity"]) else None,
                        total=float(transaction_item["Total"]) if pd.notnull(
                            transaction_item["Total"]) else None,
                        voided=bool(transaction_item["Voided"]) if pd.notnull(
                            transaction_item["Voided"]) else False,
                        paid=paid_date,
                        closed=closed_date,
                        duration_opened_to_paid=transaction_item["Duration (Opened to Paid)"] if pd.notnull(
                            transaction_item["Duration (Opened to Paid)"]) else None,
                        order_source=transaction_item["Order Source"] if pd.notnull(
                            transaction_item["Order Source"]) else None,
                    )
                )
    except Exception as e:
        logger.error(
            f"Error processing transactions check update or new instance: {e}")
        toast.error_detail = str(e)
        toast.status = ToastAuth.FAIL
        toast.save()
        raise e
    logger.info("-"*10)
    logger.info(f"َAfter, Processing {len(transactions)} transactions.")
    logger.info(
        f"After, New instances: {len(new_instances)} and updated instances: {len(updated_instances)}")
    logger.info("-"*10)
    # Use Django transaction to ensure data consistency
    with transaction.atomic():
        try:
            if new_instances:
                ToastOrder.objects.bulk_create(new_instances)
            if updated_instances:
                ToastOrder.objects.bulk_update(
                    updated_instances,
                    fields=[
                        'order_number', 'checks', 'opened', 'number_of_guests', 'tab_names', 'server', 'table',
                        'revenue_center', 'dining_area', 'service', 'dining_options', 'discount_amount',
                        'amount', 'tax', 'tip', 'gratuity', 'total', 'voided', 'paid', 'closed',
                        'duration_opened_to_paid', 'order_source'
                    ]
                )
            logger.info(
                f"Successfully processed {len(new_instances)} new transactions and updated {len(updated_instances)} existing transactions.")
        except Exception as e:
            logger.error(f"Error processing transactions: {e}")
            toast.error_detail = str(e)
            toast.status = ToastAuth.FAIL
            toast.save()
            raise e

    log_to_analytic_report(
        model_name="TOAST", status=True, error_detail="", unit=toast.unit, entry_count=len(new_instances) + len(updated_instances)
    )


# Task to crawl order details for a specific date
@shared_task(max_retries=3, default_retry_delay=10)
def crawl_toast_order_detail_by_date(toast_pk: int, date):
    """
    Crawls Toast order details for a specific date.
    Args:
        toast (ToastAuth): The ToastAuth instance.
        date (str): The date for which the order details should be crawled.
    """
    try:
        toast = ToastAuth.objects.get(pk=toast_pk)
    except ToastAuth.DoesNotExist:
        return
    filename = download_ssh_key(toast)
    logger.info(
        f"Crawling order details for date: ${date} and toast pk: {toast.pk}")
    try:
        result = ToastCrawler(
            host=toast.host,
            username=toast.username,
            location_id=toast.location_id,
            private_key_path=filename,
            date_time=date,
            file_name="OrderDetails.csv",
        ).get_data()
    except Exception as e:
        logger.error(f"Error fetching data for date {date}: {e}")
        toast.status = ToastAuth.FAIL
        toast.error_detail = str(e)
        toast.save()
        raise e

    # If the result indicates failure, log and raise an exception
    if not result["status"]:
        logger.error(
            f"Error fetching data for toast: {toast.pk} in date {date}: {result['error']}")
        toast.status = ToastAuth.FAIL
        toast.error_detail = str(
            result["error"]) if "error" in result else str(result)
        toast.save()
        raise Exception(
            result["error"] if "error" in result else "Error fetching data")

    # Process and save transactions for the specific date
    logger.info(
        f"Processing transactions for date: {date}, toast pk: {toast.pk}")
    process_transactions(result["result"], toast)

    # Trigger the upload to OpenAI after processing
    logger.info(
        f"Triggering upload to OpenAI for toast pk: {toast.pk} and unit pk:{toast.unit.pk}")
    upload_orders_openai.delay(toast.unit.pk)
