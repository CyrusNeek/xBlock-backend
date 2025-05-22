import pytest
from unittest import mock
from report.models import ToastAuth, ToastOrder, ToastPayment, ReportUser
from .tasks import crawl_toast_payment_details
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import os

# Mock current time format function
@mock.patch('report.tasks.get_current_time_format', return_value="2021-09-01")
@mock.patch('report.tasks.ToastCrawler')
@mock.patch('report.tasks.StorageService')
@mock.patch('report.tasks.logger')
@mock.patch('report.tasks.upload_payments_openai')
@mock.patch('report.tasks.crawl_toast_cash_entries')
def test_crawl_toast_payment_details_success(mock_cash_entries, mock_upload, mock_logger, mock_storage, mock_crawler, mock_time_format, django_db_setup):
    """
    Test successful crawling and saving of payment details.
    """

    # Set up mock ToastAuth object
    toast_auth = ToastAuth.objects.create(
        location_id="1234", username="testuser", host="testhost", status=ToastAuth.UNVERIFIED
    )

    # Set up mock ToastOrder object
    ToastOrder.objects.create(order_id="12345", order_number=1, toast_auth=toast_auth)

    # Mock file download (no actual file download happens)
    mock_storage().download_file.return_value = None

    # Mock data returned by the ToastCrawler
    mock_crawler().get_data.return_value = {
        "status": True,
        "result": pd.DataFrame([
            {
                "Payment Id": "P001",
                "Order Id": "12345",
                "Paid Date": "2021-09-01",
                "Order Date": "2021-09-01",
                "Check Id": "C001",
                "Check #": "1001",
                "Email": "user@example.com",
                "Phone": "1234567890",
                "Amount": "50.00",
                "Tip": "5.00",
                "Gratuity": "3.00",
                "Total": "58.00",
                "Refund Date": None,
                "Void Date": None,
                "Source": "Online",
                # More fields...
            }
        ])
    }

    # Run the task
    crawl_toast_payment_details(toast=toast_auth, is_initial_triggered=False)

    # Check if the file was downloaded
    mock_storage().download_file.assert_called_once_with(toast_auth.sshkey.private_key_location, mock.ANY)

    # Check if a ToastPayment was created
    assert ToastPayment.objects.count() == 1
    payment = ToastPayment.objects.first()
    assert payment.payment_id == "P001"
    assert payment.total == 58.00

    # Check if cash entries and upload tasks were scheduled
    mock_cash_entries.delay.assert_called_once_with(toast_auth, False, None)
    mock_upload.delay.assert_called_once_with(toast_auth.unit.pk)

    # Check logger calls
    mock_logger.info.assert_called()

    # Check if the SSH file is removed after processing
    assert not os.path.exists(mock_storage().download_file.call_args[0][1])


# Test for order not found scenario
@mock.patch('report.tasks.get_current_time_format', return_value="2021-09-01")
@mock.patch('report.tasks.ToastCrawler')
@mock.patch('report.tasks.StorageService')
@mock.patch('report.tasks.logger')
@mock.patch('report.tasks.upload_payments_openai')
@mock.patch('report.tasks.crawl_toast_cash_entries')
def test_crawl_toast_payment_details_order_not_found(mock_cash_entries, mock_upload, mock_logger, mock_storage, mock_crawler, mock_time_format, django_db_setup):
    """
    Test the case where the order referenced in payment data does not exist.
    """

    # Set up mock ToastAuth object
    toast_auth = ToastAuth.objects.create(
        location_id="1234", username="testuser", host="testhost", status=ToastAuth.UNVERIFIED
    )

    # No ToastOrder created, so it will simulate "order not found"

    # Mock file download (no actual file download happens)
    mock_storage().download_file.return_value = None

    # Mock data returned by the ToastCrawler
    mock_crawler().get_data.return_value = {
        "status": True,
        "result": pd.DataFrame([
            {
                "Payment Id": "P001",
                "Order Id": "12345",  # This order doesn't exist
                "Paid Date": "2021-09-01",
                "Order Date": "2021-09-01",
                "Check Id": "C001",
                "Check #": "1001",
                "Email": "user@example.com",
                "Phone": "1234567890",
                "Amount": "50.00",
                "Tip": "5.00",
                "Gratuity": "3.00",
                "Total": "58.00",
                "Refund Date": None,
                "Void Date": None,
                "Source": "Online",
            }
        ])
    }

    # Run the task
    crawl_toast_payment_details(toast=toast_auth, is_initial_triggered=False)

    # Ensure no payment is created since the order is missing
    assert ToastPayment.objects.count() == 0

    # Check logger calls for the order not found case
    mock_logger.error.assert_called_with("Order not found for Order Id: 12345")


# Test for exception handling
@mock.patch('report.tasks.get_current_time_format', return_value="2021-09-01")
@mock.patch('report.tasks.ToastCrawler')
@mock.patch('report.tasks.StorageService')
@mock.patch('report.tasks.logger')
@mock.patch('report.tasks.upload_payments_openai')
@mock.patch('report.tasks.crawl_toast_cash_entries')
def test_crawl_toast_payment_details_exception(mock_cash_entries, mock_upload, mock_logger, mock_storage, mock_crawler, mock_time_format, django_db_setup):
    """
    Test exception handling when an error occurs during data processing.
    """

    # Set up mock ToastAuth object
    toast_auth = ToastAuth.objects.create(
        location_id="1234", username="testuser", host="testhost", status=ToastAuth.UNVERIFIED
    )

    # Mock file download (no actual file download happens)
    mock_storage().download_file.return_value = None

    # Simulate an exception in the crawler
    mock_crawler().get_data.side_effect = Exception("Test Exception")

    # Run the task
    crawl_toast_payment_details(toast=toast_auth, is_initial_triggered=False)

    # Ensure no payment was created
    assert ToastPayment.objects.count() == 0

    # Ensure the toast status was updated to FAIL and error details were saved
    toast_auth.refresh_from_db()
    assert toast_auth.status == ToastAuth.FAIL
    assert toast_auth.error_detail == "Test Exception"

    # Check logger error call
    mock_logger.error.assert_called_with(f"Error processing payment details for ToastAuth: {toast_auth.pk}, Error: Test Exception")
