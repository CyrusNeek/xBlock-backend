import pytest
from unittest import mock
from datetime import datetime
from report.models import ToastAuth, ToastOrder
from celery.exceptions import Retry
from django.db import transaction

from report.tasks.periodic.toast.order_details_crawl import (
    crawl_toast_order_details,
    crawl_toast_order_detail_by_date,
    after_last_cronjob
)

# Mock current time format function


@mock.patch('report.tasks.get_current_time_format', return_value="2021-09-01")
@mock.patch('report.tasks.ToastCrawler')
@mock.patch('report.tasks.StorageService')
@mock.patch('report.tasks.logger')
def test_crawl_toast_order_details_initial_triggered(mock_logger, mock_storage, mock_crawler, mock_time_format, django_db_setup):
    """
    Test the task crawl_toast_order_details when it's the initial trigger.
    """

    # Set up mock ToastAuth object
    toast_auth = ToastAuth.objects.create(
        location_id="1234", username="testuser", host="testhost", status=ToastAuth.UNVERIFIED
    )

    # Set up mock SSH key file download
    mock_storage().download_file.return_value = None

    # Set up mock response for historical data
    mock_crawler().get_history.return_value = {
        "list": ["20210901", "20210902"]}

    # Mock get_data to return a successful result
    mock_crawler().get_data.return_value = {"status": True, "result": []}

    # Run the task
    crawl_toast_order_details(toast_pk=toast_auth.pk, is_initial_triggered=False)

    # Check if the file was downloaded
    mock_storage().download_file.assert_called_once_with(
        toast_auth.sshkey.private_key_location, mock.ANY)

    # Ensure the toast status is updated and saved
    toast_auth.refresh_from_db()
    assert toast_auth.status == ToastAuth.VERIFIED
    assert toast_auth.is_initial_triggered is True

    # Check that logger was called
    mock_logger.info.assert_called()

# Test case for specific date crawling


@mock.patch('report.tasks.get_current_time_format', return_value="2021-09-01")
@mock.patch('report.tasks.ToastCrawler')
@mock.patch('report.tasks.StorageService')
@mock.patch('report.tasks.logger')
def test_crawl_toast_order_detail_by_date(mock_logger, mock_storage, mock_crawler, mock_time_format, django_db_setup):
    """
    Test the task crawl_toast_order_detail_by_date for a specific date.
    """

    # Set up mock ToastAuth object
    toast_auth = ToastAuth.objects.create(
        location_id="1234", username="testuser", host="testhost", status=ToastAuth.UNVERIFIED
    )

    # Set up mock SSH key file download
    mock_storage().download_file.return_value = None

    # Mock get_data to return a successful result with mock transactions
    mock_crawler().get_data.return_value = {
        "status": True,
        "result": {
            "Opened": "2021-09-01",
            "Order Id": "12345",
            "Order #": "1001",
            "Paid": "2021-09-01",
            "Closed": "2021-09-01",
            "# of Guests": "4",
            "Checks": "Test Check"
        }
    }

    # Run the task
    crawl_toast_order_detail_by_date(toast_auth.pk, date="2021-09-01")

    # Check if the file was downloaded
    mock_storage().download_file.assert_called_once_with(
        toast_auth.sshkey.private_key_location, mock.ANY)

    # Ensure the data is processed and inserted into the database
    assert ToastOrder.objects.count() == 1
    order = ToastOrder.objects.first()
    assert order.order_id == "12345"

    # Check logger calls
    mock_logger.info.assert_called()

# Test for after_last_cronjob


@mock.patch('report.tasks.crawl_toast_payment_details')
def test_after_last_cronjob(mock_crawl_toast_payment_details, django_db_setup):
    """
    Test the task after_last_cronjob.
    """
    toast_auth = ToastAuth.objects.create(
        location_id="1234", username="testuser", host="testhost", status=ToastAuth.UNVERIFIED
    )

    # Run the task with mock dates
    after_last_cronjob(pk=toast_auth.pk, dates=["20210901", "20210902"])

    # Check if payment details task was scheduled
    mock_crawl_toast_payment_details.delay.assert_called_with(
        toast_auth, False, "20210901")
    mock_crawl_toast_payment_details.delay.assert_called_with(
        toast_auth, False, "20210902")
