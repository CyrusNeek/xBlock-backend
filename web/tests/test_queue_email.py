from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.utils import timezone

from web.models.queue_email import QueueEmail
from web.tasks.periodic_tasks.task_email import send_queued_emails


class SendQueuedEmailsTest(TestCase):

    def setUp(self):
        # Set up initial data
        self.queue_email_pending = QueueEmail.objects.create(
            email="testuser@example.com",
            subject="Test Subject",
            message="This is a test email.",
            status=1  # Pending
        )

    # Mock SendGridAPIClient
    @patch('web.tasks.sendgrid.SendGridAPIClient')
    def test_send_queued_emails_success(self, mock_sendgrid_client):
        # Mock the send method of the SendGrid client
        mock_send = MagicMock()
        mock_send.status_code = 202
        mock_sendgrid_client.return_value.send.return_value = mock_send

        # Run the Celery task
        send_queued_emails()

        # Reload the email entry from the database
        self.queue_email_pending.refresh_from_db()

        # Assertions
        # Verify that the email status was updated to "Sent" (status=2)
        self.assertEqual(self.queue_email_pending.status, 2)
        # Sent time should be updated
        self.assertIsNotNone(self.queue_email_pending.sent_at)

        # Verify that the SendGrid API was called once
        mock_sendgrid_client.return_value.send.assert_called_once()

    # Mock SendGridAPIClient
    @patch('web.tasks.sendgrid.SendGridAPIClient')
    def test_send_queued_emails_failure(self, mock_sendgrid_client):
        # Mock the send method to simulate a failure
        mock_send = MagicMock()
        mock_send.status_code = 500  # Internal server error or other failure
        mock_sendgrid_client.return_value.send.return_value = mock_send

        # Run the Celery task
        send_queued_emails()

        # Reload the email entry from the database
        self.queue_email_pending.refresh_from_db()

        # Assertions
        # Verify that the email status was updated to "Failed" (status=3)
        self.assertEqual(self.queue_email_pending.status, 3)

        # Verify that the SendGrid API was called once
        mock_sendgrid_client.return_value.send.assert_called_once()

    # Mock SendGridAPIClient
    @patch('web.tasks.sendgrid.SendGridAPIClient')
    def test_send_queued_emails_exception_handling(self, mock_sendgrid_client):
        # Mock the send method to raise an exception
        mock_sendgrid_client.return_value.send.side_effect = Exception(
            "SendGrid error")

        # Run the Celery task
        send_queued_emails()

        # Reload the email entry from the database
        self.queue_email_pending.refresh_from_db()

        # Assertions
        # Verify that the email status was updated to "Failed" (status=3) due to exception
        self.assertEqual(self.queue_email_pending.status, 3)

        # Verify that the SendGrid API was called once before the exception
        mock_sendgrid_client.return_value.send.assert_called_once()
