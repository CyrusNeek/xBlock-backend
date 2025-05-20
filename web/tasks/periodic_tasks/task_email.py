from itertools import count
import logging
from celery import shared_task
from django.utils import timezone
import sendgrid
from sendgrid.helpers.mail import Mail

from web.models.queue_email import QueueEmail
from xblock import settings


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_queued_emails(self):
    # Fetch emails with "Pending" status
    pending_emails = QueueEmail.objects.exclude(status=2)  # Not Sent

    logger.info(f"Sending {pending_emails.count()} emails")
    sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
    count_success = 0
    for email_entry in pending_emails:
        try:
            # Construct the email message using SendGrid's helper
            sender_email = settings.DEFAULT_FROM_EMAIL
            if email_entry.sender_email:
                sender_email = email_entry.sender_email

            plain_text = None
            if email_entry.type == "default":
                plain_text = email_entry.message
            message = Mail(
                from_email=sender_email,
                to_emails=email_entry.email,
                subject=email_entry.subject,
                plain_text_content=plain_text
            )

            if email_entry.type == "template":
                message.template_id = email_entry.template_id
                message.dynamic_template_data = email_entry.entry_data

            # Send the email
            response = sg.send(message)
            # Check if the email was sent successfully
            if response.status_code == 202:
                # Mark email as sent and record the sent timestamp
                email_entry.status = 2  # Sent
                email_entry.sent_at = timezone.now()
                count_success += 1
                logger.error(
                    f"email sent to {email_entry.email} successfully")
            else:
                # Mark email as failed if not successfully sent
                email_entry.status = 3  # Failed
                logger.error(
                    f"Failed to send email to {email_entry.email}: {response.body}")

        except Exception as e:
            # Mark as failed in case of any exception
            email_entry.status = 3  # Failed
            logger.error(f"Error sending email to {email_entry.email}: {str(e)}")
            # Retry the task in case of an exception
            self.retry(exc=e)

        # Save the status update back to the database
        email_entry.save()
