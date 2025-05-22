from django.conf import settings

from report.models import (
    ToastAuth
)

from report.models.toast_cash_transaction import ToastCashTransaction
from .order_details_crawl import crawl_toast_order_details
from celery import shared_task


import time




@shared_task
def task_fetch_toasts_data():
    toast_auth = ToastAuth.objects.exclude(status=ToastAuth.FAIL)
    sleep_time = settings.CRAWL_BASE_CRAWL_SLEEP_IDLE_SECONDS
    
    for toast in toast_auth:
        crawl_toast_order_details.delay(toast.pk, toast.is_initial_triggered)
        time.sleep(sleep_time)
