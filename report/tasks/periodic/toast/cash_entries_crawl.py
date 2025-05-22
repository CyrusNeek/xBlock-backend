from django.conf import settings
from django.utils import timezone

from .crawler import ToastCrawler, safe_float, get_current_time_format, input_format
from .item_selection_details_crawl import crawl_toast_item_selection_details

from report.models import ToastAuth, ToastCashTransaction

from celery import shared_task


from datetime import datetime

import os


@shared_task
def crawl_toast_cash_entries(toast: ToastAuth, is_initial_triggered, date=None):
    # filename = f'tmp-{toast.pk}.pem'

    # S3Client.s3_client.download_file(
    #     settings.AWS_STORAGE_BUCKET_NAME,
    #     toast.sshkey.private_key_location,
    #     filename
    # )

    # result = ToastCrawler(
    #    host=toast.host,
    #    username=toast.username,
    #    location_id=toast.location_id,
    #    private_key_path=filename,
    #    date_time=date if date != None else None if is_initial_triggered is False else get_current_time_format(),
    #    file_name='CashEntries.csv',
    # ).get_data()

    # # os.remove(filename)

    # df = result["result"]

    # transactions = df.to_dict(orient='records')

    # df.columns = [
    #     'location', 'entry_id', 'created_date', 'action', 'amount',
    #     'cash_drawer', 'payout_reason', 'no_sale_reason', 'comment',
    #     'employee', 'employee_2'
    # ]

    # transaction_instances = []

    # for transaction in transactions:
    #     created_date = datetime.strptime(transaction['Created Date'], input_format)

    #     transaction_instances.append(
    #         ToastCashTransaction(
    #             toast=toast,
    #             entry_id=transaction['Entry Id'],
    #             created_date=created_date,
    #             action=transaction['Action'],
    #             amount=transaction['Amount'],
    #             cash_drawer=transaction['Cash Drawer'],
    #             payout_reason=transaction['Payout Reason'],
    #             no_sale_reason=transaction['No Sale Reason'],
    #             comment=transaction['Comment'],
    #             employee=transaction['Employee'],
    #             employee_2=transaction['Employee 2']
    #         )
    #     )

    # ToastCashTransaction.objects.bulk_create(transaction_instances, ignore_conflicts=True)

    crawl_toast_item_selection_details.delay(toast, toast.is_initial_triggered, date)
